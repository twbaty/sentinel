import json
import time
import threading
import paho.mqtt.client as mqtt

STATE_TOPIC = "sentinel/livingroom/fan_light/state"
COMMAND_TOPIC = "sentinel/livingroom/fan_light/command"

current_state = {"power": "off"}


def publish_state():
    client.publish(STATE_TOPIC, json.dumps(current_state))
    print(f"[VirtualFanLight] Published state: {current_state}")


def on_connect(client, userdata, flags, rc):
    print("[VirtualFanLight] Connected.")
    client.subscribe(COMMAND_TOPIC)
    publish_state()


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    action = payload.get("action")

    print(f"[VirtualFanLight] Received command: {payload}")

    if action == "on":
        current_state["power"] = "on"
    elif action == "off":
        current_state["power"] = "off"

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
