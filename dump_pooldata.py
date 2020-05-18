from os import path
from datetime import datetime
from csv import writer

import pool_data as pd

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
                      'GPU Temperature'])

with open(csv_name, 'a') as f:
    csv = writer(f)
    csv.writerow([datetime.now().isoformat(),
                  pd.temperature(pd.POOL_TEMP_SENSOR),
                  pd.temperature(pd.SURFACE_TEMP_SENSOR),
                  pd.temperature(pd.AIR_TEMP_SENSOR),
                  pd.light_intensity(),
                  pd.pressure(pd.FILTER_PRESSURE_CHANNEL),
                  pd.powerconsumption(pd.POWER_CONSUMPTION_CHANNEL),
                  pd.pump_status(),
                  pd.cpu_temperature(),
                  pd.gpu_temperature()
                 ])
