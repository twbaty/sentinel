import json
import time
import paho.mqtt.client as mqtt

STATE_TOPIC = "sentinel/livingroom/fan_motor/state"
COMMAND_TOPIC = "sentinel/livingroom/fan_motor/command"

state = {"power": "off"}  # start off


def publish_state(client):
    client.publish(STATE_TOPIC, json.dumps(state))
    print(f"[VirtualFanMotor] Published state: {state}")


def on_connect(client, userdata, flags, rc):
    print("[VirtualFanMotor] Connected.")
    client.subscribe(COMMAND_TOPIC)
    publish_state(client)


def on_message(client, userdata, msg):
    global state
    payload = json.loads(msg.payload.decode())
    action = payload.get("action")

    print(f"[VirtualFanMotor] Received command: {payload}")

    if action == "on":
        state["power"] = "on"
    elif action == "off":
        state["power"] = "off"

    publish_state(client)


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
