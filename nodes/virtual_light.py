import json
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
DEVICE_ID = "livingroom_light"

# Must match devices.json exactly
STATE_TOPIC = "sentinel/lights/livingroom/state"
COMMAND_TOPIC = "sentinel/lights/livingroom/command"

state = {
    "power": "off"
}


def publish_state(client):
    payload = json.dumps(state)
    client.publish(STATE_TOPIC, payload)
    print(f"[VirtualLight] Published state: {payload}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[VirtualLight] Connected to broker.")
        client.subscribe(COMMAND_TOPIC)
        print(f"[VirtualLight] Subscribed to {COMMAND_TOPIC}")
        publish_state(client)
    else:
        print("[VirtualLight] Connection failed.")


def on_message(client, userdata, msg):
    global state

    print(f"[VirtualLight] Received command: {msg.payload.decode()}")

    try:
        cmd = json.loads(msg.payload.decode())
    except:
        print("[VirtualLight] Invalid JSON command.")
        return

    action = cmd.get("action")

    if action == "on":
        state["power"] = "on"
    elif action == "off":
        state["power"] = "off"
    else:
        print("[VirtualLight] Unknown action.")
        return

    publish_state(client)


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, 1883, 60)

    print("[VirtualLight] Starting loop...")
    client.loop_forever()


if __name__ == "__main__":
    main()
