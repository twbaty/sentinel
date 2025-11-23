from flask import Flask, render_template, redirect, url_for, Response, request
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEVICES_PATH = ROOT / "hub" / "devices.json"
STATE_PATH = ROOT / "hub" / "state.json"

app = Flask(__name__)


def load_json(path, default):
    if not path.exists():
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default


@app.route("/")
def index():
    devices = load_json(DEVICES_PATH, {})
    state = load_json(STATE_PATH, {})
    return render_template("index.html", devices=devices, state=state)


@app.route("/command/<device_id>/<action>")
def send_command(device_id, action):
    """
    Dashboard → publishes to MQTT through hub.py
    We publish indirectly via sentinel/dashboard/command
    """
    import paho.mqtt.publish as publish

    payload = {
        "device_id": device_id,
        "action": action
    }
    publish.single(
        "sentinel/dashboard/command",
        json.dumps(payload),
        hostname="localhost"
    )
    return redirect(url_for("index"))


@app.route("/events")
def events():
    """
    Server-Sent Events stream → pushes live device state updates
    """
    def event_stream():
        last_state = {}

        while True:
            state = load_json(STATE_PATH, {})

            if state != last_state:
                yield f"data: {json.dumps(state)}\n\n"
                last_state = state

            time.sleep(1)

    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, port=5050)
