from os import path
from datetime import datetime
from csv import writer

from pool_status import PoolStatus

csv_name = '/home/pi/Documents/pooldata_{0:%Y-%m-%d}.csv'.format(datetime.now())

if not path.exists(csv_name):
    with open(csv_name, 'w') as f:
        csv = writer(f)
        csv.writerow(['Time',
                      'Pool Temperature',
                      'Surface Temperature',
                      'Air Temperature',
                      'Light Intensity',
                      'Filter Pressure',
                      'Power Consumption',
                      'Pump Status',
                      'CPU Temperature',
                      'GPU Temperature',
                      'Wifi Quality',
                      'Wifi Max'])

ps = PoolStatus.load()

with open(csv_name, 'a') as f:
    csv = writer(f)
    csv.writerow([datetime.now().isoformat(),
                  ps.temperature['water'],
                  ps.temperature['surface'],
                  ps.temperature['air'],
                  ps.light,
                  ps.pump['pressure'],
                  ps.pump['power'],
                  ps.pump['status'],
                  ps.temperature['cpu'],
                  ps.temperature['gpu'],
                  ps.wifiquality['current'],
                  ps.wifiquality['max']])
