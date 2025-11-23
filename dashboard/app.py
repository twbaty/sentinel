from flask import Flask, render_template, redirect, url_for, Response
import json
import os
import time

# ---------------------------------------------------------
# Correct paths
# ---------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB_DIR = os.path.join(ROOT_DIR, "hub")

STATE_PATH = os.path.join(HUB_DIR, "state.json")
DEVICES_PATH = os.path.join(HUB_DIR, "devices.json")

app = Flask(__name__)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def load_devices():
    try:
        with open(DEVICES_PATH) as f:
            return json.load(f)
    except:
        return {}

def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except:
        return {}


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.route("/")
def index():
    devices = load_devices()
    state = load_state()
    return render_template("index.html", devices=devices, state=state)


@app.route("/command/<device_id>/<action>")
def send_command(device_id, action):
    """
    For now this just writes a request file that the hub watches.
    Later this will publish MQTT directly from the dashboard.
    """
    request_path = os.path.join(HUB_DIR, "requests.json")

    try:
        with open(request_path, "r") as f:
            data = json.load(f)
    except:
        data = {}

    data[device_id] = {"action": action}

    with open(request_path, "w") as f:
        json.dump(data, f, indent=2)

    return redirect(url_for("index"))


# ---------------------------------------------------------
# Server-Sent Events (SSE) for live updates
# ---------------------------------------------------------

def stream_states():
    last = ""
    while True:
        try:
            with open(STATE_PATH) as f:
                current = f.read()
        except:
            current = ""

        if current != last:
            last = current
            yield f"data: {current}\n\n"

        time.sleep(0.5)


@app.route("/events")
def events():
    return Response(stream_states(), mimetype="text/event-stream")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5050)
