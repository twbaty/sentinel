from flask import Flask, render_template, redirect, url_for
import json
import os

# Paths
HUB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hub")
STATE_PATH = os.path.join(HUB_DIR, "state.json")
DEVICES_PATH = os.path.join(HUB_DIR, "devices.json")

app = Flask(__name__)


def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except:
        return {}


def load_devices():
    with open(DEVICES_PATH) as f:
        return json.load(f)


@app.route("/")
def index():
    devices = load_devices()
    state = load_state()
    return render_template("index.html", devices=devices, state=state)


@app.route("/command/<device_id>/<action>")
def send(device_id, action):
    # Publish command by writing to a sentinel command topic
    from sentinel.hub.hub import send_command

    send_command(device_id, {"action": action})
    return redirect(url_for('index'))


@app.route("/api/state")
def api_state():
    return load_state()


if __name__ == "__main__":
    app.run(debug=True, port=5050)
