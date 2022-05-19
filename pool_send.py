from sys import exit
from time import sleep
import paho.mqtt.client as mqtt
import pool_data as pd

client = mqtt.Client("pool_data")
client.connect("localhost")
client.loop_start()

while True:
    try:
        client.publish("sensors/pool/temperature/water", pd.temperature(pd.POOL_TEMP_SENSOR), qos=2)
        client.publish("sensors/pool/temperature/surface", pd.temperature(pd.SURFACE_TEMP_SENSOR), qos=2)
        client.publish("sensors/pool/temperature/air", pd.temperature(pd.AIR_TEMP_SENSOR), qos=2)
        client.publish("sensors/pool/temperature/cpu", pd.cpu_temperature(), qos=2)
        client.publish("sensors/pool/temperature/gpu", pd.gpu_temperature(), qos=2)
        client.publish("sensors/pool/light", pd.light_intensity(), qos=2)
        client.publish("sensors/pool/pump", pd.pump_status(), qos=2)
    except KeyboardInterrupt:
        client.loop_stop()
        exit(0)
    sleep(60)

