#!/usr/bin/env python3
from flask import Flask, render_template, Response
import json
import paho.mqtt.client as mqtt
from pathlib import Path
import queue

ROOT = Path(__file__).resolve().parent
DEVICES_PATH = ROOT.parent / "hub" / "devices.json"

app = Flask(__name__, template_folder="templates")

# In-memory state
devices = {}
live_state = {}
event_queue: "queue.Queue[str]" = queue.Queue()


def load_devices():
    global devices
    with open(DEVICES_PATH) as f:
        devices = json.load(f)


# ---------------- MQTT ----------------

def on_mqtt_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    try:
        data = json.loads(payload)
    except Exception:
        return

    # Map topic → device
    for name, info in devices.items():
        if topic == info["topics"]["state"]:
            live_state[name] = data
            # SSE payload: { "name": "livingroom_light", "state": {...} }
            event_queue.put(json.dumps({"name": name, "state": data}))
            return


load_devices()

mqtt_client = mqtt.Client(client_id="sentinel_dashboard")
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect("localhost", 1883, 60)

# Subscribe to all state topics
for name, info in devices.items():
    mqtt_client.subscribe(info["topics"]["state"])

mqtt_client.loop_start()


# ---------------- Routes ----------------

@app.route("/")
def index():
    return render_template("index.html", devices=devices, live_state=live_state)


@app.route("/command/<device>/<action>")
def command(device, action):
    if device not in devices:
        return ("Unknown device", 404)

    topic = devices[device]["topics"]["command"]
    payload = json.dumps({"action": action})
    mqtt_client.publish(topic, payload)
    # No redirect → no page jump
    return ("", 204)


@app.route("/events")
def events():
    def event_stream():
        while True:
            msg = event_queue.get()
            yield f"data: {msg}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
