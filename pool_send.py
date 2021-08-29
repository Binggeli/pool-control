from sys import exit
from time import sleep
import paho.mqtt.client as mqtt
import pool_data as pd

client = mqtt.Client("pool_data")
client.connect("localhost")
client.loop_start()

while True:
    try:
        client.publish("pool/sensors/temperature/water", pd.temperature(pd.POOL_TEMP_SENSOR), qos=2)
    except KeyboardInterrupt:
        client.loop_stop()
        exit(0)
    sleep(60)
