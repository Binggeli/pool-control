from os import path
from subprocess import run, PIPE

import Adafruit_ADS1x15

POOL_TEMP_SENSOR = r'28-000008aa92f7'
AIR_TEMP_SENSOR = r'28-0416a5b761ff'
FILTER_PRESSURE_CHANNEL = 0
PUMP_SWITCH_CHANNEL = '26'

W1_DEVICE_PATH = r'/sys/devices/w1_bus_master1'


def temperature(address):
    "Return temperature read from sensor with address"
    with open(path.join(W1_DEVICE_PATH, address, 'w1_slave'), 'rt') as f:
        lines = f.readlines()
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

def pump_status():
    "Return the status of the pump"
    return run(['gpio', '-g', 'read', PUMP_SWITCH_CHANNEL],
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
    return out[5:-3]


if __name__ == "__main__":
    print('Pool temperature: ', temperature(POOL_TEMP_SENSOR))
    print('Air temperature: ', temperature(AIR_TEMP_SENSOR))
    print('Filter pressure: ', pressure(FILTER_PRESSURE_CHANNEL))
    print('Pump status: ', pump_status())
    print('CPU temperature: ', cpu_temperature())
    print('GPU temperature: ', gpu_temperature())

