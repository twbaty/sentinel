#!/usr/bin/env python3
import json
import paho.mqtt.client as mqtt
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEVICES_PATH = ROOT / "devices.json"
STATE_PATH = ROOT / "state.json"
RULES_PATH = ROOT / "rules.json"

# -------------------------------------------------------------
# Load devices
# -------------------------------------------------------------
with open(DEVICES_PATH) as f:
    devices = json.load(f)

# Live state tracked in memory
state = {name: None for name in devices.keys()}

# Load rules (optional)
try:
    with open(RULES_PATH) as f:
        rules = json.load(f)
except FileNotFoundError:
    rules = {}


# -------------------------------------------------------------
# Save state to state.json
# -------------------------------------------------------------
def save_state():
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


# -------------------------------------------------------------
# MQTT Callbacks
# -------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
    print("[Sentinel] Connected to MQTT broker.")
    client.subscribe("sentinel/#")
    print("[Sentinel] Subscribed to sentinel/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    # Try JSON decode
    try:
        data = json.loads(payload)
    except:
        print("[Sentinel] Invalid JSON:", payload)
        return

    # Find which device this message belongs to
    for dev_name, dev_info in devices.items():
        if topic == dev_info["topics"]["state"]:
            # Update memory state
            state[dev_name] = data
            print(f"[Sentinel] Updated state for {dev_name}: {data}")

            # Write-through save
            save_state()

            return


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
def main():
    print(f"[Sentinel] Loaded devices: {', '.join(devices.keys())}")
    print("[Sentinel] Hub running...")

    client = mqtt.Client(userdata={"devices": devices, "state": state})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost")
    client.loop_forever()


if __name__ == "__main__":
    main()
