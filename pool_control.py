r"""
Pool Control
------------

The algorithm to control the pool, i.e. mainly the pump, follows those steps:
    If data-object is None:
        Load data from json-file to previous data
    else:
        copy data-object to previous data
    Update data-object:
        update timestamp
        read all sensors
    if temp < min-temp or 18:00 between previous-timestamp and timestamp:
        min-temp = temp
    if temp > max-temp or 6:00 between previous-timestamp and timestamp:
        max-temp = temp
    if pump is on:
         actual runtime += (timestamp - previous-timestamp)
    target runtime as function of temperature
    remaining runtime = target runtime - actual runtime
    if ((timestamp > day-end-time - remaining runtime) or
        (light > lower-threshold if pump is on else higher-threshold) or 
        (timestamp < manual-end-time)): pump on
    else: pump off
    save data to json-file

The manual control can be taken with different priorities:
    Short term with highest priority:
        change status for 5 minutes
    Long term with lower priority:
        change status for 8 hours (after adding chemicals)
"""

from datetime import datetime, timedelta
from pathlib import Path
import os
import json

from pooldata import status_dict
from pump import run_pump

DATAPATH = Path.home() / "Documents"
LATESTDATAPATH = DATAPATH / "latestdata.json"
MANUALDATAPATH = DATAPATH / "manual"
LIGHT_TRESHOLD = {False: 25000, True: 15000}

def pumptime(temperature):
    """Return the target runtime in hours for the given temperature.

    This is based on the recommendation:
    - 16-24 C: 12 Std.
    - 25-28 C: 16 Std.
    -   >28 C: 24 Std.
    """
    pumphours = max(min(((0.016835*temperature - 0.97643)*temperature + 18.912)*temperature - 109.58,
                        24),
                    0)
    return timedelta(hours=pumphours)

def load_data():
    "Return the latest data object loaded from the json file."
    data = json.load(LATESTDATAPATH.read_text())
    return data

def save_data(data, timestamp, latest=True):
    """Save data object as a json file.

    The filename contains the timestamp of the data object.
    If latest is True (default) a symbolic link is created
    with the name "latestdata".
    """
    datafile = DATAPATH / "data_{:%Y%m%d%H%M%S}.json".format(timestamp)
    with datafile.open("wt") as datastream:
        json.dump(data, datastream)
    if latest:
        os.symlink(str(datafile),
                   str(LATESTDATAPATH))

def load_manual_control(timestamp):
    "Return manual control status based on manual control data files."
    data = [json.load(datafile.read_text()) for datafile in MANUALDATAPATH.glob("*.json")]
    data = [d for d in data if d.starttime <= timestamp and timestamp < d.stoptime]
    if data.empty:
        return None
    else:
        return max(d, key=lambda d: d.priority).status

def next_time(timestamp, hour=0, minute=0, second=0, microsecond=0):
    "Return the next point in time with the given local hour/minute/second."
    next = timestamp.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)
    if next < timestamp:
        next = next + timedelta(days=1)
    return next

def control_pool(curr_data):
    "Main loop to control the pool pump"
    if curr_data is None:
        prev_data = load_data()
    else:
        prev_data = curr_data
    curr_data = status_dict()
    # update min and max temperatures
    reset_min = (curr_data['timestamp'] > next_time(prev_data['timestamp'], hour=18))
    for sensor in curr_data['temperature']:
        if curr_data['temperature'][sensor] < curr_data['min-temperature'][sensor] or reset_min:
            curr_data['min-temperature'][sensor] = curr_data['temperature'][sensor]
    reset_max = (curr_data['timestamp'] > next_time(prev_data['timestamp'], hour=6))
    for sensor in curr_data['temperature']:
        if curr_data['temperature'][sensor] > curr_data['min-temperature'][sensor] or reset_max:
            curr_data['min-temperature'][sensor] = curr_data['temperature'][sensor]
    # update pump runtime
    if curr_data['timestamp'] <= next_time(prev_data['timestamp'], hour=6):
        curr_data['pump']['runtime'] = prev_data['pump']['runtime']
    else:
        curr_data['pump']['runtime'] = timedelta(hours=0)
    if prev_data['pump']['status'] == True:
        curr_data['pump']['runtime'] += curr_data['timestamp'] - prev_data['timestamp']
    # update pump status
    curr_data['pump']['target_runtime'] = pumphours(curr_data['temperature']['water'])
    runtime = curr_data['pump']['target_runtime'] - curr_data['pump']['runtime']
    if not manual_control is None:
        run_pump(manual_control)
    elif (curr_data['timestamp'] > next_time(curr_data['timestamp'], hour=6) - runtime or
        curr_data['light'] > LIGHT_THRESHOLD[curr_data['pump']['status']]):
        run_pump(True)
    else:
        run_pump(False)
    curr_data['pump']['status'] = pooldata.pump_status()
    # save dict to json file
    save_data(curr_data, curr_data['timestamp'], latest=True)
    return curr_data


if __name__ == "__main__":
    print('Temperature   Pump runtime')
    for temp in range(30):
        print('{0:12}: {1}'.format(temp, pumptime(temp)))
    control_pool(None)
