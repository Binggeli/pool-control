import json
import paho.mqtt.client as mqtt

# Define the callback for when a message is received
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        flag = data.get('flag')
        value1 = data.get('value1')
        value2 = data.get('value2')

        if isinstance(flag, bool) and isinstance(value1, int) and isinstance(value2, int):
            print(f"Received - Flag: {flag}, Value1: {value1}, Value2: {value2}")
        else:
            print("Invalid data types in message.")

    except json.JSONDecodeError:
        print("Received message is not valid JSON.")

# Set up the MQTT client
client = mqtt.Client()

client.on_message = on_message

# Connect to the broker
client.connect("localhost", 1883, 60)

# Subscribe to the topic
client.subscribe("test/topic")

# Start the loop to process network traffic and dispatch callbacks
print("Listening for messages on 'test/topic'...")
client.loop_forever()
