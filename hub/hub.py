import json
import os
import time
import paho.mqtt.client as mqtt

# -------------------------------------------------------
# Paths
# -------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
REGISTRY_PATH = os.path.join(BASE_DIR, "devices.json")
STATE_PATH = os.path.join(BASE_DIR, "state.json")

# -------------------------------------------------------
# Load device registry
# -------------------------------------------------------

with open(REGISTRY_PATH, "r") as f:
    DEVICES = json.load(f)

print("[Sentinel] Loaded devices:", ", ".join(DEVICES.keys()))

# -------------------------------------------------------
# Load persistent state
# -------------------------------------------------------

try:
    with open(STATE_PATH, "r") as f:
        DEVICE_STATE = json.load(f)
except:
    DEVICE_STATE = {}


def save_state():
    with open(STATE_PATH, "w") as f:
        json.dump(DEVICE_STATE, f, indent=2)

RULES_PATH = os.path.join(BASE_DIR, "rules.json")

try:
    with open(RULES_PATH, "r") as f:
        RULES = json.load(f)
except:
    RULES = []

RULES_PATH = os.path.join(BASE_DIR, "rules.json")

try:
    with open(RULES_PATH, "r") as f:
        RULES = json.load(f)
except:
    RULES = []


# -------------------------------------------------------
# MQTT Handlers
# -------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Sentinel] Connected to MQTT broker.")
        client.subscribe("sentinel/#")
        print("[Sentinel] Subscribed to: sentinel/#")
    else:
        print(f"[Sentinel] MQTT connection failed (rc={rc}).")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()

    # Only print meaningful messages
    print(f"[MQTT] {msg.topic} → {payload}")

    try:
        data = json.loads(payload)
    except:
        return  # ignore non-JSON messages

    handle_message(msg.topic, data)


# -------------------------------------------------------
# Message Handler
# -------------------------------------------------------

def handle_message(topic, data):
    """
    Handle incoming state messages.
    Sentinel ignores command topics.
    """

    for device_id, device in DEVICES.items():
        if topic == device["topics"]["state"]:
            DEVICE_STATE[device_id] = data
            save_state()
            print(f"[Sentinel] Updated state for {device_id}: {data}")
            return

    # Ignore anything that doesn't map to a state topic
    return


# -------------------------------------------------------
# Publish Commands
# -------------------------------------------------------

def send_command(device_id, command_dict):
    device = DEVICES.get(device_id)
    if not device:
        print(f"[Sentinel] Unknown device: {device_id}")
        return

    topic = device["topics"]["command"]
    payload = json.dumps(command_dict)

    mqtt_client.publish(topic, payload)
    print(f"[Sentinel] Sent command to {device_id}: {payload}")


# -------------------------------------------------------
# Startup
# -------------------------------------------------------

def run_hub():
    global mqtt_client

    print("[Sentinel] Starting hub...")

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect("localhost", 1883, 60)

    mqtt_client.loop_forever()


if __name__ == "__main__":
    run_hub()
