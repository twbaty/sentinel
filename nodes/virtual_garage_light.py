import json
import time
import threading
import paho.mqtt.client as mqtt

DEVICE_NAME = "VirtualGarageLight"
STATE_TOPIC = "sentinel/garage/light/state"
COMMAND_TOPIC = "sentinel/garage/light/command"

current_state = {"power": "off"}
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
    publish_state()


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    action = payload.get("action")
    print(f"[{DEVICE_NAME}] Received command: {payload}")

    if action == "on":
        current_state["power"] = "on"
    elif action == "off":
        current_state["power"] = "off"

    publish_state()


def heartbeat():
    while True:
        time.sleep(1)
        publish_state()


def main():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)

    threading.Thread(target=heartbeat, daemon=True).start()
    client.loop_forever()


if __name__ == "__main__":
    main()
