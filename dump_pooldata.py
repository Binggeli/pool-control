from os import path
from datetime import datetime
from csv import writer

import pooldata

csv_name = '/home/pi/Documents/pooldata_{0:%Y-%m-%d}.csv'.format(datetime.now())

if not path.exists(csv_name):
    with open(csv_name, 'w') as f:
        csv = writer(f)
        csv.writerow(['Time',
                      'Pool Temperature',
                      'Air Temperature',
                      'Filter Pressure',
                      'Pump Status',
                      'CPU Temperature',
                      'GPU Temperature'])

with open(csv_name, 'a') as f:
    csv = writer(f)
    csv.writerow([datetime.now().isoformat(),
                  pooldata.temperature(pooldata.POOL_TEMP_SENSOR),
                  pooldata.temperature(pooldata.AIR_TEMP_SENSOR),
                  pooldata.pressure(pooldata.FILTER_PRESSURE_CHANNEL),
                  pooldata.pump_status(),
                  pooldata.cpu_temperature(),
                  pooldata.gpu_temperature()
                 ])
