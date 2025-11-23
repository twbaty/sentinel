#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

ROOT = Path(__file__).resolve().parent
DEVICES_PATH = ROOT / "devices.json"
STATE_PATH = ROOT / "state.json"
LOG_PATH = ROOT / "events.log"

# ------------------------
# Load devices + init state
# ------------------------
with open(DEVICES_PATH) as f:
    devices = json.load(f)

state = {name: None for name in devices.keys()}


# ------------------------
# Helpers
# ------------------------
def save_state():
    """Persist current state to state.json."""
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def log_event(message: str):
    """Append a timestamped line to events.log."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{ts}] {message}\n")


def apply_rules(device_name: str, new_state: dict, client: mqtt.Client):
    """
    Very simple rules engine.

    For now:
      - If garage_door_main position becomes 'closed',
        send 'off' command to garage_light.
    """
    if device_name == "garage_door_main":
        position = new_state.get("position")
        if position == "closed" and "garage_light" in devices:
            topic = devices["garage_light"]["topics"]["command"]
            payload = {"action": "off"}
            client.publish(topic, json.dumps(payload))
            print("[Rules] Garage door closed → garage_light OFF")
            log_event("Rule fired: garage_door_main closed → garage_light OFF")


# ------------------------
# MQTT callbacks
# ------------------------
def on_connect(client, userdata, flags, rc):
    print("[Sentinel] Connected to MQTT broker.")
    client.subscribe("sentinel/#")
    print("[Sentinel] Subscribed to sentinel/#")
    log_event("Hub connected to MQTT and subscribed to sentinel/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    try:
        data = json.loads(payload)
    except Exception:
        print("[Sentinel] Invalid JSON:", payload)
        log_event(f"Invalid JSON on {topic}: {payload!r}")
        return

    # Map topic → device
    for dev_name, dev_info in devices.items():
        if topic == dev_info["topics"]["state"]:
            state[dev_name] = data
            print(f"[Sentinel] Updated state for {dev_name}: {data}")
            log_event(f"State updated: {dev_name} → {data}")
            save_state()
            apply_rules(dev_name, data, client)
            return


# ------------------------
# Main
# ------------------------
def main():
    print(f"[Sentinel] Loaded devices: {', '.join(devices.keys())}")
    log_event(f"Hub starting. Devices: {', '.join(devices.keys())}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
