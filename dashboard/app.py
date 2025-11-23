from flask import Flask, render_template, redirect, url_for
import json
import sys
import paho.mqtt.client as mqtt
from queue import Queue

app = Flask(__name__, template_folder="templates")

# Shared queue for SSE events
event_queue = Queue()

### MQTT Setup ###
mqtt_client = mqtt.Client(client_id="sentinel_dashboard")
mqtt_client.connect("localhost")
mqtt_client.loop_start()      # <<< REQUIRED

### Load device configuration ###
DEVICES_PATH = "hub/devices.json"

def load_devices():
    with open(DEVICES_PATH) as f:
        return json.load(f)

@app.route("/")
def index():
    devices = load_devices()
    return render_template("index.html", devices=devices)

@app.route("/command/<device>/<action>")
def command(device, action):
    devices = load_devices()

    if device not in devices:
        return redirect(url_for("index"))

    topic = devices[device]["topics"]["command"]
    payload = json.dumps({"action": action})

    mqtt_client.publish(topic, payload)
    print(f"[Dashboard] Published → {topic}: {payload}")

    return redirect(url_for("index"))

### Server-Sent Events ###
@app.route("/events")
def events():
    def generator():
        while True:
            data = event_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    return app.response_class(generator(), mimetype="text/event-stream")

### Main entry ###
if __name__ == "__main__":
    use_reloader = "--no-reload" not in sys.argv
    debug_mode = not use_reloader

    print(f"[Dashboard] Starting (reloader={use_reloader})")

    app.run(
        host="127.0.0.1",
        port=5050,
        debug=debug_mode,
        use_reloader=use_reloader
    )
