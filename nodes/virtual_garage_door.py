import json
import time
import paho.mqtt.client as mqtt

STATE_TOPIC = "sentinel/garage/main_door/state"
COMMAND_TOPIC = "sentinel/garage/main_door/command"

state = {"position": "closed"}  # initial value


def publish_state(client):
    client.publish(STATE_TOPIC, json.dumps(state))
    print(f"[VirtualGarageDoor] Published state: {state}")


def on_connect(client, userdata, flags, rc):
    print("[VirtualGarageDoor] Connected.")
    client.subscribe(COMMAND_TOPIC)
    publish_state(client)


def on_message(client, userdata, msg):
    global state
    payload = json.loads(msg.payload.decode())
    action = payload.get("action")

    print(f"[VirtualGarageDoor] Received command: {payload}")

    if action == "open":
        state["position"] = "open"
    elif action == "close":
        state["position"] = "closed"

    publish_state(client)


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
