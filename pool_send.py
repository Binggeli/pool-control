from sys import exit
from time import sleep
import paho.mqtt.client as mqtt
import pool_data as pd

client = mqtt.Client("pool_data")
client.connect("localhost")
client.loop_start()

# add discovery messages for Home Assistant
config = """
{"device_class": "temperature",
 "name": "Wassertemperatur",
 "state_topic": "sensors/pool/temperature/water",
 "value_template": "{{ value }}",
 "unit_of_measurement": "°C"}
"""
client.publish("homeassistant/sensor/pool/water/config", config, qos=2, retain=True)

while True:
    try:
        client.publish("sensors/pool/temperature/water", pd.temperature(pd.POOL_TEMP_SENSOR), qos=2)
        client.publish("sensors/pool/temperature/surface", pd.temperature(pd.SURFACE_TEMP_SENSOR), qos=2)
        client.publish("sensors/pool/temperature/air", pd.temperature(pd.AIR_TEMP_SENSOR), qos=2)
        client.publish("sensors/pool/temperature/cpu", pd.cpu_temperature(), qos=2)
        client.publish("sensors/pool/temperature/gpu", pd.gpu_temperature(), qos=2)
        client.publish("sensors/pool/light", pd.light_intensity(), qos=2)
        client.publish("sensors/pool/pump", pd.pump_status(), qos=2)
        client.publish("sensors/pool/throttled", pd.throttled(), qos=2)
        client.publish("sensors/pool/uptime", pd.uptime(), qos=2)
    except KeyboardInterrupt:
        client.loop_stop()
        exit(0)
    sleep(60)

