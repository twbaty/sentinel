import paho.mqtt.client as mqtt
import json

BROKER = "localhost"
STATE_TOPIC = "sentinel/garage/main/state"
CMD_TOPIC = "sentinel/garage/main/command"

position = "closed"


def publish_state(client):
    payload = json.dumps({"position": position})
    client.publish(STATE_TOPIC, payload)
    print(f"[VirtualGarage] Published state: {payload}")


def on_message(client, userdata, msg):
    global position

    try:
        data = json.loads(msg.payload.decode())
    except:
        return

    action = data.get("action")
    if not action:
        return

    if action == "open":
        position = "open"
    elif action == "close":
        position = "closed"
    else:
        return

    publish_state(client)


def main():
    client = mqtt.Client()
    client.on_message = on_message

    client.connect(BROKER)
    client.subscribe(CMD_TOPIC)

    client.loop_start()

    print("[VirtualGarage] Running. Waiting for commands...")
    publish_state(client)

    while True:
        pass
import threading, time, json

def heartbeat():
    while True:
        time.sleep(1)
        client.publish(STATE_TOPIC, json.dumps(current_state))

threading.Thread(target=heartbeat, daemon=True).start()


if __name__ == "__main__":
    main()
