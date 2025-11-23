import json
import time
import threading
import paho.mqtt.client as mqtt

STATE_TOPIC = "sentinel/garage/main_door/state"
COMMAND_TOPIC = "sentinel/garage/main_door/command"

current_state = {"position": "closed"}  # up/down states


def publish_state():
    client.publish(STATE_TOPIC, json.dumps(current_state))
    print(f"[VirtualGarageDoor] Published state: {current_state}")


def on_connect(client, userdata, flags, rc):
    print("[VirtualGarageDoor] Connected.")
    client.subscribe(COMMAND_TOPIC)
    publish_state()


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    action = payload.get("action")
    print(f"[VirtualGarageDoor] Received command: {payload}")

    if action == "open":
        current_state["position"] = "open"
    elif action == "close":
        current_state["position"] = "closed"

    publish_state()


def heartbeat():
    while True:
        time.sleep(1)
        publish_state()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


def main():
    client.connect("localhost", 1883, 60)
    threading.Thread(target=heartbeat, daemon=True).start()
    client.loop_forever()


if __name__ == "__main__":
    main()
