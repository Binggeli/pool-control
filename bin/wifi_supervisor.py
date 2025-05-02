from subprocess import call, DEVNULL
from time import sleep

MQTT_HOST = 'mqtt.sunnig.ch'


def supervise_wifi():
    """Restart the dhcpcd service, which is responsible for the wifi connection."""
    if call(['ping', '-c', '1', MQTT_HOST], stdout=DEVNULL) != 0:
        print('No connection, restarting dhcpcd service.')
        call(['sudo', 'systemctl', 'restart', 'dhcpcd'])


if __name__ == '__main__':
    while True:
        supervise_wifi()
        sleep(60)
