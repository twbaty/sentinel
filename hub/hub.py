#!/usr/bin/env python3
import json
import paho.mqtt.client as mqtt
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEVICES_PATH = ROOT / "devices.json"
STATE_PATH = ROOT / "state.json"

# Load devices
with open(DEVICES_PATH) as f:
    devices = json.load(f)

# Live state store
state = {name: None for name in devices.keys()}


def save_state():
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def on_connect(client, userdata, flags, rc):
    print("[Hub] Connected to MQTT")
    client.subscribe("sentinel/#")
    print("[Hub] Subscribed to sentinel/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    try:
        data = json.loads(payload)
    except:
        print("[Hub] Invalid JSON:", payload)
        return

    # Match state topic → device
    for dev_name, dev_info in devices.items():
        if topic == dev_info["topics"]["state"]:
            state[dev_name] = data
            print(f"[Hub] Updated {dev_name}: {data}")
            save_state()
            return


def main():
    print("[Hub] Loaded devices:", ", ".join(devices.keys()))
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
