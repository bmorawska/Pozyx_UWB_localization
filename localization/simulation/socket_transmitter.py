import socketio
import time
import math

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://192.168.178.129:3000')

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
