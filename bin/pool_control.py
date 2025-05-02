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

from time import sleep
from datetime import datetime, time, timedelta
from pathlib import Path
from pprint import pprint
import logging
import logging.handlers

from pool_status import PoolStatus
from pool_trigger import PoolTrigger
from pump import run_pump
import pool_data as pd

LIGHT_THRESHOLD = {False: 5000, True: 1000}

LOGGER = logging.getLogger(__name__)


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

def load_manual_control(timestamp):
    "Return manual control status based on manual control data files."
    trg = PoolTrigger.load(timestamp=timestamp)
    if trg is None:
        return None
    else:
        return trg.status

def next_time(timestamp, hour=0, minute=0, second=0, microsecond=0):
    "Return the next point in time with the given local hour/minute/second."
    next = timestamp.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)
    if next < timestamp:
        next = next + timedelta(days=1)
    return next

def control_pool(status):
    "Main loop to control the pool pump"
    if status is None:
        status = PoolStatus.load()
    prev_timestamp = status.timestamp
    status.update()
    # update min and max temperatures
    reset_min = (status.timestamp > next_time(prev_timestamp, hour=18))
    for sensor in status.temperature:
        if (sensor not in status.min_temperature or
            status.temperature[sensor] < status.min_temperature[sensor] or
            reset_min):
            LOGGER.debug('Resetting min for %s from %s to %s (%s)', sensor,
                         status.min_temperature[sensor] if sensor in status.min_temperature else '-',
                         status.temperature[sensor] if sensor in status.temperature else '-',
                         reset_min)
            status.min_temperature[sensor] = status.temperature[sensor]
    reset_max = (status.timestamp > next_time(prev_timestamp, hour=6))
    for sensor in status.temperature:
        if (sensor not in status.max_temperature or
            status.temperature[sensor] > status.max_temperature[sensor] or
            reset_max):
            status.max_temperature[sensor] = status.temperature[sensor]
    # update pump runtime
    if status.timestamp > next_time(prev_timestamp, hour=6):
        status.pump['runtime'] = timedelta(hours=0)
    if status.pump['status'] == True:
        status.pump['runtime'] += status.timestamp - prev_timestamp
    # update pump status
    status.pump['target_runtime'] = pumptime(status.max_temperature['water'])
    runtime = status.pump['target_runtime'] - status.pump['runtime']
    # load manual pool triggers:
    manual_control = load_manual_control(status.timestamp)
    if not manual_control is None:
        LOGGER.debug('Running pump based on manual trigger: %s', manual_control)
        run_pump(manual_control)
    elif status.light > LIGHT_THRESHOLD[status.pump['status']]:
        LOGGER.debug('Running pump due to sunlight %s', status.light)
        run_pump(True)
    elif status.timestamp > next_time(status.timestamp, hour=6) - runtime:
        LOGGER.debug('Running pump to reach remaining target runtime %s', runtime)
        run_pump(True)
    else:
        run_pump(False)
    status.pump['status'] = pd.pump_status()
    # save dict to json file
    status.save()
    return status

def main():
    "Run the main loop forever"
    status = None
    try:
        while True:
            status = control_pool(status)
            sleep(10)
    except Exception as exception:
        LOGGER.exception('Exception in main loop of pool control at %s: %s', datetime.now(), exception)
        return


if __name__ == "__main__":
    handler = logging.handlers.TimedRotatingFileHandler('/var/log/pool/control.log',
                                                        when='midnight', atTime=time(6))
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.DEBUG)
    main()
