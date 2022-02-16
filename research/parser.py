import argparse
import json
import time
import pandas as pd
import os
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Translate from strange JSON to xslx')
parser.add_argument('--input', default='.', help="input folder")
parser.add_argument('--output', default='output', help='output folder')
args = parser.parse_args()

INPUT = args.input
OUTPUT = args.output

if not os.path.exists(OUTPUT):
    os.mkdir(OUTPUT)

files = os.listdir(INPUT)

for file in tqdm(files):
    if '.json' not in file:
        continue
    path = os.path.join(INPUT, file)
    with open(path) as f:
        line = f.read()

    first_sign = line.find("{")
    msg = '{\"data\":['
    msg += line[first_sign:].replace(" ", ""). \
        replace("\n", ""). \
        replace(",", ',\"'). \
        replace(":", '\":'). \
        replace(":{", ':{\"'). \
        replace("}{", "},{")

    msg = msg.replace(":[{", ':[{\"'). \
        replace(",{x", ',{\"x'). \
        replace(",{time", ',{\"time'). \
        replace('\"\"', '\"')

    msg += ']}'

    json_msg = json.loads(msg)

    version = []
    alive = []
    tagId = []
    success = []
    timestamp = []
    data__tagData__gyro__x = []
    data__tagData__gyro__y = []
    data__tagData__gyro__z = []
    data__tagData__magnetic__x = []
    data__tagData__magnetic__y = []
    data__tagData__magnetic__z = []
    data__tagData__quaternion__x = []
    data__tagData__quaternion__y = []
    data__tagData__quaternion__z = []
    data__tagData__quaternion__w = []
    data__tagData__linearAcceleration__x = []
    data__tagData__linearAcceleration__y = []
    data__tagData__linearAcceleration__z = []
    data__tagData__pressure = []
    data__tagData__maxLinearAcceleration = []
    data__anchorData = []
    data__acceleration__x = []
    data__acceleration__y = []
    data__acceleration__z = []
    data__orientation__yaw = []
    data__orientation__roll = []
    data__orientation__pitch = []
    data__metrics__latency = []
    data__metrics__rates__update = []
    data__metrics__rates__success = []
    data__coordinates__x = []
    data__coordinates__y = []
    data__coordinates__z = []

    for j in json_msg["data"]:
        version.append(1)
        alive.append(1)
        tagId.append(26437)
        success.append(1)
        try:
            t = j["time"]
        except KeyError:
            t = time.time()
        timestamp.append(t)
        data__tagData__gyro__x.append(j["angular_vel"]["x"])
        data__tagData__gyro__y.append(j["angular_vel"]["y"])
        data__tagData__gyro__z.append(j["angular_vel"]["z"])
        data__tagData__magnetic__x.append(j["magnetic"]["x"])
        data__tagData__magnetic__y.append(j["magnetic"]["y"])
        data__tagData__magnetic__z.append(j["magnetic"]["z"])
        data__tagData__quaternion__x.append(j["quaternion"]["x"])
        data__tagData__quaternion__y.append(j["quaternion"]["y"])
        data__tagData__quaternion__z.append(j["quaternion"]["z"])
        data__tagData__quaternion__w.append(j["quaternion"]["w"])
        data__tagData__linearAcceleration__x.append(j["linear_acceleration"]["x"])
        data__tagData__linearAcceleration__y.append(j["linear_acceleration"]["y"])
        data__tagData__linearAcceleration__z.append(j["linear_acceleration"]["z"])
        data__tagData__pressure.append(j["pressure"])
        data__tagData__maxLinearAcceleration.append(
            max(
                max(data__tagData__linearAcceleration__x),
                max(data__tagData__linearAcceleration__x),
                max(data__tagData__linearAcceleration__x)
            )
        )
        data__anchorData.append(None)
        data__acceleration__x.append(j["acceleration"]["x"])
        data__acceleration__y.append(j["acceleration"]["y"])
        data__acceleration__z.append(j["acceleration"]["z"])
        data__orientation__yaw.append(j["euler_angles"]["heading"])
        data__orientation__roll.append(j["euler_angles"]["roll"])
        data__orientation__pitch.append(j["euler_angles"]["pitch"])
        if len(timestamp) == 1:
            data__metrics__latency.append(t - timestamp[-1])
        else:
            data__metrics__latency.append(t - timestamp[-2])
        data__metrics__rates__update.append(20)
        data__metrics__rates__success.append(20)
        data__coordinates__x.append(j["x"])
        data__coordinates__y.append(j["y"])
        data__coordinates__z.append(120)

    column_names = [
        "version",
        "alive",
        "tagId",
        "success",
        "timestamp",
        "data__tagData__gyro__x",
        "data__tagData__gyro__y",
        "data__tagData__gyro__z",
        "data__tagData__magnetic__x",
        "data__tagData__magnetic__y",
        "data__tagData__magnetic__z",
        "data__tagData__quaternion__x",
        "data__tagData__quaternion__y",
        "data__tagData__quaternion__z",
        "data__tagData__quaternion__w",
        "data__tagData__linearAcceleration__x",
        "data__tagData__linearAcceleration__y",
        "data__tagData__linearAcceleration__z",
        "data__tagData__pressure",
        "data__tagData__maxLinearAcceleration",
        "data__anchorData",
        "data__acceleration__x",
        "data__acceleration__y",
        "data__acceleration__z",
        "data__orientation__yaw",
        "data__orientation__roll",
        "data__orientation__pitch",
        "data__metrics__latency",
        "data__metrics__rates__update",
        "data__metrics__rates__success",
        "data__coordinates__x",
        "data__coordinates__y",
        "data__coordinates__z"
    ]
    df = pd.DataFrame(columns=column_names)

    df["version"] = version
    df["alive"] = alive
    df["tagId"] = tagId
    df["success"] = success
    df["timestamp"] = timestamp
    df["data__tagData__gyro__x"] = data__tagData__gyro__x
    df["data__tagData__gyro__y"] = data__tagData__gyro__y
    df["data__tagData__gyro__z"] = data__tagData__gyro__z
    df["data__tagData__magnetic__x"] = data__tagData__magnetic__x
    df["data__tagData__magnetic__y"] = data__tagData__magnetic__y
    df["data__tagData__magnetic__z"] = data__tagData__magnetic__z
    df["data__tagData__quaternion__x"] = data__tagData__quaternion__x
    df["data__tagData__quaternion__y"] = data__tagData__quaternion__y
    df["data__tagData__quaternion__z"] = data__tagData__quaternion__z
    df["data__tagData__quaternion__w"] = data__tagData__quaternion__w
    df["data__tagData__linearAcceleration__x"] = data__tagData__linearAcceleration__x
    df["data__tagData__linearAcceleration__y"] = data__tagData__linearAcceleration__y
    df["data__tagData__linearAcceleration__z"] = data__tagData__linearAcceleration__z
    df["data__tagData__pressure"] = data__tagData__pressure
    df["data__tagData__maxLinearAcceleration"] = data__tagData__maxLinearAcceleration
    df["data__anchorData"] = data__anchorData
    df["data__acceleration__x"] = data__acceleration__x
    df["data__acceleration__y"] = data__acceleration__y
    df["data__acceleration__z"] = data__acceleration__z
    df["data__orientation__yaw"] = data__orientation__yaw
    df["data__orientation__roll"] = data__orientation__roll
    df["data__orientation__pitch"] = data__orientation__pitch
    df["data__metrics__latency"] = data__metrics__latency
    df["data__metrics__rates__update"] = data__metrics__rates__update
    df["data__metrics__rates__success"] = data__metrics__rates__success
    df["data__coordinates__x"] = data__coordinates__x
    df["data__coordinates__y"] = data__coordinates__y
    df["data__coordinates__z"] = data__coordinates__z
    df["data__coordinates__x"] *= 1000
    df["data__coordinates__y"] *= 1000

    output_filename = file.split('.')[0] + '.xlsx'
    df.to_excel(os.path.join(OUTPUT, output_filename))
