#!/usr/bin/env python
import argparse
from time import sleep
from pypozyx import (Coordinates, 
                     PozyxConstants,
                     DeviceCoordinates, 
                     PozyxSerial, 
                     get_first_pozyx_serial_port)
from pypozyx.tools.version_check import perform_latest_version_check
import socketio


import ReadyToLocalize

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, required=False, default='localhost', help='Node server ip address.')
parser.add_argument('--web', action='store_true', required=False, help='Send data to web visualization')
parser.set_defaults(noweb=False)
args = parser.parse_args()

if args.web:
    sio = socketio.Client()

    @sio.event
    def connect():
        print('connection established')

    @sio.event
    def disconnect():
        print('disconnected from server')

anchors = []

if __name__ == "__main__":
    # Check for the latest PyPozyx version. Skip if this takes too long or is not needed by setting to False.
    check_pypozyx_version = True
    if check_pypozyx_version:
        perform_latest_version_check()

    # shortcut to not have to find out the port yourself
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    remote_id = None                # remote device network ID
    remote = False                   # whether to use a remote device
    if not remote:
        remote_id = None

    connected = False

    if args.web:
        while not connected:
            try:
                sio.connect(f'http://{args.ip}:3000') #server ip - change here
                connected = True
            except socketio.exceptions.ConnectionError:
                print("Cannot establish connection. Next try in 5 secs.")
            sleep(5)

    # necessary data for calibration
    with open('anchors.csv', 'r') as file:
        lines = file.readlines()
    for line in lines:
        anchor = line.split()
        anchors.append(DeviceCoordinates(anchor[0], 1, Coordinates(anchor[1], anchor[2], anchor[3])))

    # positioning algorithm to use, other is PozyxConstants.POSITIONING_ALGORITHM_TRACKING
    algorithm = PozyxConstants.POSITIONING_ALGORITHM_TRACKING
    # positioning dimension. Others are PozyxConstants.DIMENSION_2D, PozyxConstants.DIMENSION_2_5D
    dimension = PozyxConstants.DIMENSION_2D
    # height of device, required in 2.5D positioning
    height = 1000

    pozyx = PozyxSerial(serial_port)
    r = ReadyToLocalize(pozyx, sio, anchors, algorithm, dimension, height, remote_id, args.web)
    r.setup()
    while True:
        r.loop()