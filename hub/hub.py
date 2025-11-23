import json
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sentinel/#"   # Sentinel listens only to its own namespace


# ----------------------------
# MQTT EVENT HANDLERS
# ----------------------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Sentinel] Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
        print(f"[Sentinel] Subscribed to: {MQTT_TOPIC}")
    else:
        print(f"[Sentinel] Connection failed. RC={rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} → {payload}")

    # Try parsing as JSON
    try:
        data = json.loads(payload)
        handle_message(msg.topic, data)
    except json.JSONDecodeError:
        print("[Sentinel] Non-JSON payload, ignoring.")


# ----------------------------
# SENTINEL MESSAGE HANDLER
# ----------------------------

def handle_message(topic, data):
    """
    This is where Sentinel will later:
    - update device states
    - trigger automation rules
    - route commands to nodes
    - log events
    """

    print(f"[Sentinel] Handling message on {topic}")
    print(f"[Sentinel] Data: {data}")


# ----------------------------
# MAIN LOOP
# ----------------------------

def run_hub():
    print("[Sentinel] Starting hub...")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    run_hub()

