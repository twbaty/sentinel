import json
import paho.mqtt.client as mqtt
import os

def send_command(device_id, command_dict):
    device = DEVICES.get(device_id)
    if not device:
        print(f"[Sentinel] Unknown device: {device_id}")
        return

    topic = device["topics"]["command"]
    payload = json.dumps(command_dict)

    mqtt_client.publish(topic, payload)
    print(f"[Sentinel] Sent command to {device_id}: {payload}")


REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "devices.json")

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sentinel/#"   # Sentinel listens only to its own namespace

with open(REGISTRY_PATH, "r") as f:
    DEVICES = json.load(f)

print("[Sentinel] Loaded devices:", ", ".join(DEVICES.keys()))

# ----------------------------
# MQTT EVENT HANDLERS
# ----------------------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Sentinel] Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
        print(f"[Sentinel] Subscribed to: {MQTT_TOPIC}")
    else:
        print(f"[Sentinel] Connection failed. RC={rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} → {payload}")

    # Try parsing as JSON
    try:
        data = json.loads(payload)
        handle_message(msg.topic, data)
    except json.JSONDecodeError:
        print("[Sentinel] Non-JSON payload, ignoring.")


# ----------------------------
# SENTINEL MESSAGE HANDLER
# ----------------------------

def handle_message(topic, data):
    for device_id, device in DEVICES.items():
        state_topic = device["topics"]["state"]

        if topic == state_topic:
            device["last_state"] = data
            print(f"[Sentinel] Updated state for {device_id}: {data}")
            return

    # silently ignore any non-state messages
    return


    print(f"[Sentinel] Handling message on {topic}")
    print(f"[Sentinel] Data: {data}")


# ----------------------------
# MAIN LOOP
# ----------------------------

def run_hub():
    global mqtt_client

    print("[Sentinel] Starting hub...")

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

    mqtt_client.loop_forever()

if __name__ == "__main__":
    run_hub()

