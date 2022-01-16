from pypozyx import DeviceCoordinates, Coordinates
import csv
import os
import json

anchors = []
remote_tags = []
device_coordinates = []
sendable_anchors = None

def load_anchors():
    filename = 'anchors.csv'
    sendable_anchors = []
    with open(os.path.join('data', filename)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader, None) 
        for row in csv_reader:
            id = int(row[0], 16)
            isAnchor = bool(row[1])
            x = int(row[2])
            y = int(row[3])
            z = int(row[4])

            coordinates = Coordinates(x, y, z)
            sendable_anchors.append({"id": id, "x": x, "y": y})
            device_coordinates.append(DeviceCoordinates(network_id=id, flag=isAnchor, pos=coordinates))
            anchors.append(id)

            if isAnchor == 1:
                dev_str = 'anchor'
            else:
                dev_str = 'tag'

            print(f"[{id} as {dev_str}]:\tx:{x}\ty={y}\tz={z}")

        sendable_anchors = json.dumps(sendable_anchors)
        print(f'File {filename} loaded succesfully.')

