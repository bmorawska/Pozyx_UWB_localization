import socketio
import time
import math
import argparse

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
        
    sio.connect(f'http://{args.ip}:3000')

ox = 5
oy = 5
angle = 0
radius = 4
anchors = []

with open('anchors.csv', 'r') as file:
    lines = file.readlines()
for line in lines:
    anchor = line.split()
    anchors.append(anchor)

if args.web:
    sio.emit('anchors', {'anchors': anchors})

while True:
    x = ox + math.cos(angle) * radius
    y = oy + math.sin(angle) * radius
    angle += 0.01
    if args.web:
        sio.emit('position', {'x': x, 'y': y})
    else:
        print(f"['x': {x}, 'y': {y}]")
    time.sleep(0.01)
