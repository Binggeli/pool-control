r"""
Pool Control
------------

The algorithm to control the pool, i.e. mainly the pump, follows those steps:
    If data-object is None:
        Load data from json-file
    Update data-object:
        copy timestamp to previous-timestamp
        update timestamp
        read all sensors
    if temp < min-time or 18:00 between previous-timestamp and timestamp:
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
"""

from datetime import datetime, timedelta
import json
#import pooldata
#from pump import run_pump

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





if __name__ == "__main__":
    print('Temperature   Pump runtime')
    for temp in range(30):
        print('{0:12}: {1}'.format(temp, pumptime(temp)))
