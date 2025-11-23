#!/usr/bin/env python3
from flask import Flask, render_template, Response, redirect, url_for
import json
import paho.mqtt.client as mqtt
from pathlib import Path
import queue

ROOT = Path(__file__).resolve().parent
DEVICES_PATH = ROOT.parent / "hub" / "devices.json"
STATE_PATH = ROOT.parent / "hub" / "state.json"

# In-memory state for live updates
live_state = {}
event_queue = queue.Queue()

app = Flask(__name__, template_folder="templates")


# Load devices
def load_devices():
    with open(DEVICES_PATH) as f:
        return json.load(f)


# MQTT callbacks
def on_mqtt_message(client, userdata, msg):
    global live_state
    topic = msg.topic
    payload = msg.payload.decode()

    try:
        data = json.loads(payload)
    except:
        return

    # Update running state and broadcast to browser
    for dev, info in devices.items():
        if topic == info["topics"]["state"]:
            live_state[dev] = data
            event_queue.put(json.dumps({dev: data}))
            return


# Setup MQTT
devices = load_devices()
mqtt_client = mqtt.Client(client_id="sentinel_dashboard")
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect("localhost", 1883, 60)

# Subscribe to all state topics
for d, inf in devices.items():
    mqtt_client.subscribe(inf["topics"]["state"])

mqtt_client.loop_start()


@app.route("/")
def index():
    return render_template("index.html", devices=devices, live_state=live_state)


@app.route("/command/<device>/<action>")
def command(device, action):
    if device not in devices:
        return redirect(url_for("index"))

    topic = devices[device]["topics"]["command"]
    mqtt_client.publish(topic, json.dumps({"action": action}))
    return redirect(url_for("index"))


@app.route("/events")
def events():
    def event_stream():
        while True:
            msg = event_queue.get()
            yield f"data: {msg}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
