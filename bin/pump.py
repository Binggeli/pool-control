from argparse import ArgumentParser
import logging
import RPi.GPIO as GPIO

from pool_data import temperature, POOL_TEMP_SENSOR, PUMP_SWITCH_CHANNEL, BULB_SWITCH_CHANNEL


def run_pump(state):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for channel in [PUMP_SWITCH_CHANNEL, BULB_SWITCH_CHANNEL]:
        GPIO.setup(int(channel), GPIO.OUT)
        GPIO.output(int(channel), state)

def argparser():
    """Create an argument parser for the command line."""
    parser = ArgumentParser(description='Change pump state based on arguments and sensors.')
    parser.add_argument('-f', '--force', help='force the specified state regardless of sensor readings.')
    parser.add_argument(dest='state', choices=['on', 'off'],
                        help='Change pump to the specified state.')
    return parser

if __name__ == "__main__":
    args = argparser().parse_args()
    if args.state == 'on':
        logging.info('Switching pump on')
        run_pump(True)
    elif (temperature(POOL_TEMP_SENSOR) < 25 or args.force):
        logging.info('Switching pump off')
        run_pump(False)
