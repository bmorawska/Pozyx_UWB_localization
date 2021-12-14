#!/usr/bin/env python
from time import sleep
from pypozyx import (POZYX_POS_ALG_UWB_ONLY,
                     POZYX_3D, 
                     Coordinates, 
                     POZYX_SUCCESS, 
                     PozyxConstants,
                     version,
                     DeviceCoordinates, 
                     PozyxSerial, 
                     get_first_pozyx_serial_port, 
                     SingleRegister, 
                     DeviceList, 
                     PozyxRegisters)
from pypozyx.tools.version_check import perform_latest_version_check
import socketio

from devices import anchors, remote_tags

class ReadyToLocalize(object):
    """Continuously calls the Pozyx positioning function and prints its position."""

    def __init__(self, pozyx, sio, anchors, algorithm=POZYX_POS_ALG_UWB_ONLY, dimension=POZYX_3D, height=1000, remote_id=None):
        self.pozyx = pozyx
        self.sio = sio

        self.anchors = anchors
        self.algorithm = algorithm
        self.dimension = dimension
        self.height = height
        self.remote_id = remote_id

    def setup(self):
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        print("------------POZYX POSITIONING V{} -------------".format(version))
        print("")
        print("- System will manually configure tag")
        print("")
        print("- System will auto start positioning")
        print("")
        if self.remote_id is None:
            self.pozyx.printDeviceInfo(self.remote_id)
        else:
            for device_id in [None, self.remote_id]:
                self.pozyx.printDeviceInfo(device_id)
        print("")
        print("------------POZYX POSITIONING V{} -------------".format(version))
        print("")

        self.setAnchorsManual(save_to_flash=False)
        self.printPublishConfigurationResult()

    def loop(self):
        """Performs positioning and displays/exports the results."""
        position = Coordinates()
        status = self.pozyx.doPositioning(
            position, self.dimension, self.height, self.algorithm, remote_id=self.remote_id)
        if status == POZYX_SUCCESS:
            self.printPublishPosition(position)
        else:
            self.printPublishErrorCode("positioning")

    def printPublishPosition(self, position):
        """Prints the Pozyx's position and possibly sends it as a socketio packet"""
        network_id = self.remote_id
        if network_id is None:
            network_id = 0
        print("POS ID {}, x(mm): {pos.x} y(mm): {pos.y} z(mm): {pos.z}".format(
            "0x%0.4x" % network_id, pos=position))

        pos_x = int(position.x) / 1000
        pos_y = int(position.y) / 1000
        sio.emit('position', {'x': pos_x, 'y': pos_y})
      

    def printPublishErrorCode(self, operation):
        """Prints the Pozyx's error and possibly sends it as a socketio packet"""
        error_code = SingleRegister()
        network_id = self.remote_id
        if network_id is None:
            self.pozyx.getErrorCode(error_code)
            print("LOCAL ERROR %s, %s" % (operation, self.pozyx.getErrorMessage(error_code)))
            sio.emit('error', self.pozyx.getErrorMessage(error_code))
            return
        status = self.pozyx.getErrorCode(error_code, self.remote_id)
        if status == POZYX_SUCCESS:
            print("ERROR %s on ID %s, %s" %
                  (operation, "0x%0.4x" % network_id, self.pozyx.getErrorMessage(error_code)))
            sio.emit('error', self.pozyx.getErrorMessage(error_code))
        else:
            self.pozyx.getErrorCode(error_code)
            print("ERROR %s, couldn't retrieve remote error code, LOCAL ERROR %s" %
                  (operation, self.pozyx.getErrorMessage(error_code)))
            sio.emit('error', self.pozyx.getErrorMessage(error_code))
            # should only happen when not being able to communicate with a remote Pozyx.

    def setAnchorsManual(self, save_to_flash=False):
        """Adds the manually measured anchors to the Pozyx's device list one for one."""
        status = self.pozyx.clearDevices(remote_id=self.remote_id)
        for anchor in self.anchors:
            status &= self.pozyx.addDevice(anchor, remote_id=self.remote_id)
        if len(self.anchors) > 4:
            status &= self.pozyx.setSelectionOfAnchors(PozyxConstants.ANCHOR_SELECT_AUTO, len(self.anchors),
                                                       remote_id=self.remote_id)

        if save_to_flash:
            self.pozyx.saveAnchorIds(remote_id=self.remote_id)
            self.pozyx.saveRegisters([PozyxRegisters.POSITIONING_NUMBER_OF_ANCHORS], remote_id=self.remote_id)
        return status

    def printPublishConfigurationResult(self):
        """Prints and potentially publishes the anchor configuration result in a human-readable way."""
        list_size = SingleRegister()

        self.pozyx.getDeviceListSize(list_size, self.remote_id)
        print("List size: {0}".format(list_size[0]))
        if list_size[0] != len(self.anchors):
            self.printPublishErrorCode("configuration")
            return
        device_list = DeviceList(list_size=list_size[0])
        self.pozyx.getDeviceIds(device_list, self.remote_id)
        print("Calibration result:")
        print("Anchors found: {0}".format(list_size[0]))
        print("Anchor IDs: ", device_list)

        anch = {}
        for i in range(list_size[0]):
            anchor_coordinates = Coordinates()
            self.pozyx.getDeviceCoordinates(device_list[i], anchor_coordinates, self.remote_id)
            print("ANCHOR, 0x%0.4x, %s" % (device_list[i], str(anchor_coordinates)))
            anch[device_list[i]] = [int(anchor_coordinates.x), int(anchor_coordinates.y)]

        sio.emit('anchors', anch)
        sleep(0.025)

    def printPublishAnchorConfiguration(self):
        """Prints and potentially publishes the anchor configuration"""
        anch = {}
        for anchor in self.anchors:
            print("ANCHOR,0x%0.4x,%s" % (anchor.network_id, str(anchor.coordinates)))



sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def disconnect():
    print('disconnected from server')


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

    remote_id = [0x672a, 0x673b]                # remote device network ID
    remote = False                   # whether to use a remote device
    if not remote:
        remote_id = None

    connected = False

    while not connected:
        try:
            sio.connect('http://192.168.178.129:3000')
            connected = True
        except socketio.exceptions.ConnectionError:
            print("Cannot establish connection. Next try in 5 secs.")
        sleep(5)


    # necessary data for calibration, change the IDs and coordinates yourself according to your measurement
    anchors = [DeviceCoordinates(anchors[0], 1, Coordinates(0, 0, 2790)),
               DeviceCoordinates(anchors[1], 1, Coordinates(10490, 0, 2790)),
               DeviceCoordinates(anchors[2], 1, Coordinates(-405, 6000, 2790)),
               DeviceCoordinates(anchors[3], 1, Coordinates(10490, 6500, 2790)),
               DeviceCoordinates(anchors[4], 1, Coordinates(10490, 6500, 2790)),
               DeviceCoordinates(anchors[5], 1, Coordinates(10490, 6500, 2790)),
               DeviceCoordinates(anchors[6], 1, Coordinates(10490, 6500, 2790)),
               DeviceCoordinates(anchors[7], 1, Coordinates(10490, 6500, 2790)),]

    # positioning algorithm to use, other is PozyxConstants.POSITIONING_ALGORITHM_TRACKING
    algorithm = PozyxConstants.POSITIONING_ALGORITHM_TRACKING
    # positioning dimension. Others are PozyxConstants.DIMENSION_2D, PozyxConstants.DIMENSION_2_5D
    dimension = PozyxConstants.DIMENSION_2D
    # height of device, required in 2.5D positioning
    height = 1000

    pozyx = PozyxSerial(serial_port)
    r = ReadyToLocalize(pozyx, sio, anchors, algorithm, dimension, height, remote_id)
    r.setup()
    while True:
        r.loop()