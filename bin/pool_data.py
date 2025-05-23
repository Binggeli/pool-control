import re
from time import sleep
from datetime import datetime
from pathlib import Path
from subprocess import run, PIPE

import Adafruit_ADS1x15
import smbus

POOL_TEMP_SENSOR = r'28-0213187499aa'
SURFACE_TEMP_SENSOR = r'28-000008aa92f7'
AIR_TEMP_SENSOR = r'28-0416a5b761ff'
FILTER_PRESSURE_CHANNEL = 0
POWER_CONSUMPTION_CHANNEL = 1
POWER_CONSUMPTION_MEASUREMENTS = 20
PUMP_SWITCH_CHANNEL = '26'
BULB_SWITCH_CHANNEL = '20'

W1_DEVICE_PATH = Path(r'/sys/devices/w1_bus_master1')

SMBUS = smbus.SMBus(1)


def temperature(address):
    "Return temperature read from sensor with address"
    lines = (W1_DEVICE_PATH / address / 'w1_slave').read_text().split('\n')
    if lines[0].strip()[-3:] == 'YES':
        line = lines[1].strip()
        return int(line[line.find('t=')+2:])/1000

def pressure(channel):
    """Return pressure from the pump sensor

    Conversion factor:
    - sensor: 12 bar is 5 V
    - ADC: 32767 is 4.096 V
    - 12 * 4.096 * value / 32767 / 5
    """
    adc = Adafruit_ADS1x15.ADS1115()
    value = adc.read_adc(channel, gain=1)
    return (value / 3333.23161)

def powerconsumption(channel):
    """Return power consumption of the pump

    Conversion factor:
    - sensor: 1A is 0.185V
    - ADC: 32767 is 4.096 V (gain = 1)
    - Power: 230 * 4.096/0.185 * value / 32767

    The readings are oscillating around the zero. The amplitude
    is calculated as (max - min)/2.

    The scaling factor is:
        230 * 4.096/0.185 * 1/2 * 1/32767 ~ 0.07771
    """
    adc = Adafruit_ADS1x15.ADS1115()
    adc.start_adc(channel, gain=1)
    reading = [adc.get_last_result()
               for _ in range(POWER_CONSUMPTION_MEASUREMENTS)]
    adc.stop_adc()
    return 0.07771 * (max(reading) - min(reading))

def light_intensity():
    """Return the light intensity"""
    data = SMBUS.read_i2c_block_data(0x23, 0x20)
    value = (data[1] + (256 * data[0])) / 1.2
    return value

def pump_status():
    "Return the status of the pump"
    return run(['gpio', '-g', 'read', PUMP_SWITCH_CHANNEL],
               stdout=PIPE).stdout.strip() == b'1'

def bulb_status():
    "Return the status of the UV bulb"
    return run(['gpio', '-g', 'read', BULB_SWITCH_CHANNEL],
               stdout=PIPE).stdout.strip() == b'1'

def cpu_temperature():
    "Return the temperature of the CPU"
    with open('/sys/class/thermal/thermal_zone0/temp', 'rt') as f:
        line = f.readlines()
    return int(line[0])/1000

def gpu_temperature():
    "Return the temperature of the GPU"
    out = run(['/opt/vc/bin/vcgencmd', 'measure_temp'],
              stdout=PIPE, universal_newlines=True).stdout
    return float(out[5:-3])

def throttled():
    "Return the throttling bits of the Raspberry Pi."
    out = run(['/opt/vc/bin/vcgencmd', 'get_throttled'],
              stdout=PIPE, universal_newlines=True).stdout
    return int(out[10:], 16)

def uptime():
    "Return the uptime in seconds."
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds

def wifi_signal_level():
    "Return the signal level of the wifi link."
    out = run(['/sbin/iwconfig', 'wlan0'],
              stdout=PIPE, universal_newlines=True).stdout
    m = re.search('Signal level=(-?[0-9]+) dBm', out)
    if m:
        return m.group(1)
    else:
        return None

def status_dict():
    "Return dict with current data for the pool."
    return {'temperature':
                {'water': temperature(POOL_TEMP_SENSOR),
                 'surface': temperature(SURFACE_TEMP_SENSOR),
                 'air': temperature(AIR_TEMP_SENSOR)},
            'light': light_intensity(),
            'pressure': pressure(FILTER_PRESSURE_CHANNEL),
            'pump':
                {'status': pump_status(),
                 'pressure': pressure(FILTER_PRESSURE_CHANNEL),
                 'power': powerconsumption(POWER_CONSUMPTION_CHANNEL)},
            'relay':
                {'pump': pump_status()},
            'wifi_signal_level': wifi_signal_level(),
            'timestamp': '{:%d.%m.%Y %H:%M:%S}'.format(datetime.now())}


if __name__ == "__main__":
    print('Pool temperature: ', temperature(POOL_TEMP_SENSOR))
    print('Surface temperature: ', temperature(SURFACE_TEMP_SENSOR))
    print('Air temperature: ', temperature(AIR_TEMP_SENSOR))
    print('Light intensity: ', light_intensity())
    print('Filter pressure: ', pressure(FILTER_PRESSURE_CHANNEL))
    print('Power consumption: ', powerconsumption(POWER_CONSUMPTION_CHANNEL))
    print('Pump status: ', pump_status())
    print('Bulb status: ', bulb_status())
    print('CPU temperature: ', repr(cpu_temperature()))
    print('GPU temperature: ', repr(gpu_temperature()))
    print('Throttled: ', throttled())
    print('Uptime: ', uptime())
    print('Wifi Signal Level:', wifi_signal_level())
