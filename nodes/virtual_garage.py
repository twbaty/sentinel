import paho.mqtt.client as mqtt
import json
import time

BROKER = "localhost"
STATE_TOPIC = "sentinel/garage/main/state"
CMD_TOPIC = "sentinel/garage/main/command"

position = "closed"   # default


def publish_state(client):
    payload = json.dumps({"position": position})
    client.publish(STATE_TOPIC, payload)
    print(f"[VirtualGarage] Published state: {payload}")


# Handle commands if you want future expansion
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

    print("[VirtualGarage] Running. Press ENTER to toggle.")

    publish_state(client)

    while True:
        input()  # press ENTER to toggle
        global position
        position = "open" if position == "closed" else "closed"
        publish_state(client)


if __name__ == "__main__":
    main()
