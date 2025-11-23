import os
import json
import time
import paho.mqtt.client as mqtt

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEVICES_PATH = os.path.join(BASE_DIR, "devices.json")
STATE_PATH = os.path.join(BASE_DIR, "state.json")
RULES_PATH = os.path.join(BASE_DIR, "rules.json")
REQUESTS_PATH = os.path.join(BASE_DIR, "requests.json")

# ---------------------------------------------------------
# Load Devices, State, Rules
# ---------------------------------------------------------

def load_devices():
    try:
        with open(DEVICES_PATH) as f:
            return json.load(f)
    except:
        return {}

def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def load_rules():
    try:
        with open(RULES_PATH) as f:
            return json.load(f)
    except:
        return []

# ---------------------------------------------------------
# Automation Engine
# ---------------------------------------------------------

def apply_rules(device_id, new_state, rules, mqtt_client, devices):
    for rule in rules:
        if rule.get("trigger_device") != device_id:
            continue

        field = rule.get("trigger_field")
        expected = rule.get("trigger_value")

        if new_state.get(field) != expected:
            continue

        target = rule.get("action_device")
        action = rule.get("action")
        if not target or not action:
            continue

        topic = devices[target]["topics"]["command"]
        payload = json.dumps({"action": action})

        print(f"[Sentinel] Rule match: {rule['name']}")
        mqtt_client.publish(topic, payload)

# ---------------------------------------------------------
# Dashboard Command Handling
# ---------------------------------------------------------

def check_pending_commands(mqtt_client, devices):
    try:
        with open(REQUESTS_PATH, "r") as f:
            pending = json.load(f)
    except:
        pending = {}

    if not pending:
        return

    for device_id, cmd in pending.items():
        action = cmd.get("action")
        if not action:
            continue

        topic = devices[device_id]["topics"]["command"]
        payload = json.dumps({"action": action})

        print(f"[Sentinel] Dashboard command → {device_id}: {payload}")
        mqtt_client.publish(topic, payload)

    # Clear requests after processing
    with open(REQUESTS_PATH, "w") as f:
        json.dump({}, f)

# ---------------------------------------------------------
# MQTT Callbacks
# ---------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    print("[Sentinel] Connected to MQTT broker.")
    client.subscribe("sentinel/#")
    print("[Sentinel] Subscribed to sentinel/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    try:
        data = json.loads(payload)
    except:
        return

    devices = userdata["devices"]
    state = userdata["state"]
    rules = userdata["rules"]

    # Match state topics
    for dev_id, dev in devices.items():
        if topic == dev["topics"]["state"]:
            state[dev_id] = data
            save_state(state)

            print(f"[Sentinel] Updated state for {dev_id}: {data}")

            # run automation
            apply_rules(dev_id, data, rules, client, devices)
            return

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    devices = load_devices()
    state = load_state()
    rules = load_rules()

    print(f"[Sentinel] Loaded devices: {', '.join(devices.keys())}")

    client = mqtt.Client(userdata={"devices": devices, "state": state, "rules": rules})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost")
    client.loop_start()

    print("[Sentinel] Hub running...")

    # Main loop → check dashboard commands
    while True:
        check_pending_commands(client, devices)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
