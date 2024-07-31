from sys import exit
from time import sleep
import paho.mqtt.client as mqtt
import pool_data as pd

client = mqtt.Client("pool_data")
client.connect("localhost")
client.loop_start()

with open('/sys/class/net/wlan0/address', 'rt') as f:
    mac = f.read().strip()
if len(mac) != 17 or mac.count(':') != 5:
    mac = mac.replace('-', '')
    mac = mac.replace('.', '')
    if len(mac) == 12:
        mac = ':'.join(mac.lower()[i:i+2] for i in range(0, 12, 2))
print('Mac address: {0}'.format(mac))

# add discovery messages for Home Assistant
config = """
{{"unique_id": "{0}_{1}",
  "device_class": "temperature",
  "name": "{2}",
  "state_topic": "sensors/pool/temperature/{1}",
  "value_template": "{{{{ value }}}}",
  "unit_of_measurement": "°C"}}
"""

client.publish("homeassistant/sensor/pool/water/config",
    config.format(mac, 'water', 'Wassertemperatur'),
    qos=2, retain=True)
client.publish("homeassistant/sensor/pool/air/config",
    config.format(mac, 'air', 'Aussentemperatur'),
    qos=2, retain=True)
client.publish("homeassistant/sensor/pool/surface/config",
    config.format(mac, 'surface', 'Oberflächentemperatur'),
    qos=2, retain=True)

# add discovery messages for Home Assistant
config = """
{{"unique_id": "{0}_{1}",
  "device_class": "illuminance",
  "name": "{2}",
  "state_topic": "sensors/pool/{1}",
  "value_template": "{{{{ value }}}}",
  "unit_of_measurement": "lx"}}
"""

client.publish("homeassistant/sensor/pool/light/config",
    config.format(mac, 'light', 'Sonneneinstrahlung'),
    qos=2, retain=True)

# add discovery messages for Home Assistant
config = """
{{"unique_id": "{0}_{1}",
  "name": "{2}",
  "state_topic": "sensors/pool/{1}",
  "payload_on": "True",
  "payload_off": "False"}}
"""

client.publish("homeassistant/binary_sensor/pool/pump/config",
    config.format(mac, 'pump', 'Pumpe'),
    qos=2, retain=True)

# add discovery messages for Home Assistant
config = """
{{"unique_id": "{0}_{1}",
  "device_class": "signal_strength",
  "name": "{2}",
  "state_topic": "sensors/pool/{1}",
  "value_template": "{{{{ value }}}}",
  "unit_of_measurement": "dBm"}}
"""

client.publish("homeassistant/sensor/pool/wifi_signal_level/config",
    config.format(mac, 'wifi_signal_level', 'Wifi Signal Level'),
    qos=2, retain=True)

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
        client.publish("sensors/pool/wifi_signal_level", pd.wifi_signal_level(), qos=2)
    except KeyboardInterrupt:
        client.loop_stop()
        exit(0)
    sleep(60)

