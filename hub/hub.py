import json
import time
import threading
import paho.mqtt.client as mqtt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEVICES_PATH = ROOT / "hub" / "devices.json"
STATE_PATH = ROOT / "hub" / "state.json"
RULES_PATH = ROOT / "hub" / "rules.json"

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def load_json(path, default):
    if not path.exists():
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------------------------------------------------------
# Device Class Behavior Map
# ---------------------------------------------------------------------

# Defines what actions a class supports, and what state fields it uses.
CLASS_BEHAVIORS = {

    "light": {
        "valid_actions": ["on", "off"],
        "state_field": "power"
    },

    "fan": {
        "valid_actions": ["on", "off"],
        "state_field": "power"
    },

    "garage_door": {
        "valid_actions": ["open", "close"],
        "state_field": "position"
    }
}

# ---------------------------------------------------------------------
# MQTT Callbacks
# ---------------------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    print("[Sentinel] Connected to MQTT broker.")
    client.subscribe("sentinel/#")
    print("[Sentinel] Subscribed to sentinel/#")

def on_message(client, userdata, msg):
    devices = userdata["devices"]
    state = userdata["state"]

    topic = msg.topic
    payload_raw = msg.payload.decode()

    # Dashboard-origin messages:
    if topic == "sentinel/dashboard/command":
        try:
            packet = json.loads(payload_raw)
        except:
            return

        device_id = packet.get("device_id")
        action = packet.get("action")

        if not device_id or device_id not in devices:
            print(f"[Sentinel] Dashboard → invalid device: {device_id}")
            return

        device_class = devices[device_id]["class"]
        behavior = CLASS_BEHAVIORS.get(device_class)

        if not behavior:
            print(f"[Sentinel] No behavior for class '{device_class}'")
            return

        # Validate the action against the class
        if action not in behavior["valid_actions"]:
            print(f"[Sentinel] Invalid action '{action}' for class '{device_class}'")
            return

        # Forward action to actual device topic
        command_topic = devices[device_id]["topics"]["command"]
        packet = { "action": action }
        client.publish(command_topic, json.dumps(packet))

        print(f"[Sentinel] Dashboard command → {device_id}: {packet}")
        return

    # State updates from devices:
    for device_id, device in devices.items():
        if topic == device["topics"]["state"]:
            try:
                data = json.loads(payload_raw)
            except:
                return

            state[device_id] = data
            save_json(STATE_PATH, state)

            print(f"[Sentinel] Updated state for {device_id}: {data}")
            return

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    devices = load_json(DEVICES_PATH, {})
    state = load_json(STATE_PATH, {})
    rules = load_json(RULES_PATH, {})

    print("[Sentinel] Loaded devices:", ", ".join(devices.keys()))

    mqtt_client = mqtt.Client(userdata={
        "devices": devices,
        "state": state,
        "rules": rules
    })

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect("localhost", 1883, 60)

    print("[Sentinel] Hub running...")
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
