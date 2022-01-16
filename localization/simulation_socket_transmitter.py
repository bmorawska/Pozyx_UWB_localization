import socketio
import time
import math
import argparse
import os

from devices import load_anchors, sendable_anchors

sio = socketio.Client()
load_anchors()


@sio.event
def connect():
    print('connection established')

@sio.event
def disconnect():
    print('disconnected from server')


@sio.on('anchors')
def on_message(data):
    sio.emit('anchors', sendable_anchors)
    print('Anchors position sent')


parser = argparse.ArgumentParser(description='Pozyx localization program.')
parser.add_argument('-i','--ip', help='Description for foo argument', default='localhost')
args = parser.parse_args()

ip = args.ip

env = os.getenv("IP_ADDRESS")
if env is not None:
    ip = env

sio.connect(f'http://{ip}:3000')

ox = 5
oy = 5
angle = 0
radius = 4

while True:
    x = ox + math.cos(angle) * radius
    y = oy + math.sin(angle) * radius
    angle += 0.01

    sio.emit('position', {'x': x, 'y': y})
    time.sleep(0.01)
