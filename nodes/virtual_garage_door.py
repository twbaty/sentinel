import json
import time
import threading
import paho.mqtt.client as mqtt

DEVICE_NAME = "VirtualGarageDoor"
STATE_TOPIC = "sentinel/garage/main_door/state"
COMMAND_TOPIC = "sentinel/garage/main_door/command"

current_state = {"position": "closed"}
last_published_state = None

client = mqtt.Client()


def publish_state():
    global last_published_state
    if current_state != last_published_state:
        client.publish(STATE_TOPIC, json.dumps(current_state))
        print(f"[{DEVICE_NAME}] Published state: {current_state}")
        last_published_state = current_state.copy()


def on_connect(client, userdata, flags, rc):
    print(f"[{DEVICE_NAME}] Connected.")
    client.subscribe(COMMAND_TOPIC)
    publish_state()  # initial publish


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    action = payload.get("action")
    print(f"[{DEVICE_NAME}] Received command: {payload}")

    if action == "open":
        current_state["position"] = "open"
    elif action == "close":
        current_state["position"] = "closed"

    publish_state()


def heartbeat():
    while True:
        time.sleep(1)
        publish_state()  # only publishes if state changed


def main():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)

    threading.Thread(target=heartbeat, daemon=True).start()
    client.loop_forever()


if __name__ == "__main__":
    main()
