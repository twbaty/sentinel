#!/usr/bin/env python3
from flask import Flask, render_template, redirect, url_for
import json
import sys
import paho.mqtt.client as mqtt
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEVICES_PATH = ROOT.parent / "hub" / "devices.json"
STATE_PATH = ROOT.parent / "hub" / "state.json"

app = Flask(__name__, template_folder="templates")


# -------------------------------------------------------
# MQTT CLIENT
# -------------------------------------------------------
mqtt_client = mqtt.Client(client_id="sentinel_dashboard")
mqtt_client.connect("localhost")
mqtt_client.loop_start()


# -------------------------------------------------------
# Load device definitions
# -------------------------------------------------------
def load_devices():
    with open(DEVICES_PATH) as f:
        return json.load(f)


# -------------------------------------------------------
# Load live state (written by hub)
# -------------------------------------------------------
def load_live_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except:
        return {}


# -------------------------------------------------------
# Routes
# -------------------------------------------------------
@app.route("/")
def index():
    devices = load_devices()
    live_state = load_live_state()

    # Merge live state into devices
    for dev_name, info in devices.items():
        info["last_state"] = live_state.get(dev_name)

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


# -------------------------------------------------------
# Main
# -------------------------------------------------------
if __name__ == "__main__":
    use_reloader = "--no-reload" not in sys.argv
    debug_mode = not use_reloader

    print(f"[Dashboard] Starting (reloader={use_reloader})")

    app.run(
        host="127.0.0.1",
        port=5050,
        debug=debug_mode,
        use_reloader=use_reloader,
    )
