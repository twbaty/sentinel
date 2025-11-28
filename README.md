# sentinel

Sentinel: Modular MQTT-Driven Home Automation Sandbox

Sentinel is a lightweight, modular home-automation simulation platform.
It includes:

A central Hub (rules engine, state manager)

Multiple Virtual Devices (garage door, lights, fan motor/light)

A real-time Dashboard (Flask + Server-Sent Events)

A simple Automation Engine (rules.json)

A multi-process launcher (run_all.py)

The entire environment runs locally and communicates via MQTT.

Sentinel is designed as a learning platform for event-driven IoT systems, automation logic, and distributed device behaviors.

📦 Project Structure
sentinel/
│
├── hub/
│   ├── hub.py           # Central rules engine + state tracking
│   ├── devices.json     # Device metadata + MQTT topics
│   ├── state.json       # Last-known state for every device
│   └── rules.json       # Automation rules (if/then)
│
├── dashboard/
│   ├── app.py           # Flask frontend + SSE event stream
│   └── templates/
│       └── index.html   # Tile-based UI for all devices
│
├── nodes/
│   ├── virtual_garage_door.py
│   ├── virtual_garage_light.py
│   ├── virtual_livingroom_light.py
│   ├── virtual_fan_motor.py
│   └── virtual_fan_light.py
│
├── run_all.py           # Launch hub, dashboard, and all virtual devices
└── README.md            # You are here

🚀 Running Sentinel

Start everything with one command:

python run_all.py


This launches:

MQTT hub

Flask dashboard

All virtual device processes

Heartbeat threads (devices publish state once per second)

Dashboard runs at:

http://127.0.0.1:5050

📡 How Sentinel Works

Sentinel follows a simple event-driven pipeline:

Virtual Device → MQTT → Hub → Rules Engine → MQTT → Device → Dashboard (SSE)

1. Virtual Device

Each node:

connects to MQTT

subscribes to its command topic

publishes its state every 1s

updates state on commands (“on”, “off”, “open”, “close”)

2. Hub

The hub:

subscribes to all sentinel/# topics

updates state.json

checks every state change against rules.json

publishes command actions for matching rules

3. Dashboard

The dashboard:

loads state.json on initial load

listens on /events for real-time updates via SSE

updates UI elements instantly

shows ON/OFF or OPEN/CLOSED indicators

allows issuing commands to devices

🧠 Automation Rules (rules.json)

Rules are evaluated only when device state changes.

Example:

[
  {
    "if": {
      "topic": "sentinel/garage/main_door/state",
      "equals": {"position": "open"}
    },
    "then": {
      "device": "garage_light",
      "action": "on"
    }
  },
  {
    "if": {
      "topic": "sentinel/garage/main_door/state",
      "equals": {"position": "closed"}
    },
    "then": {
      "device": "garage_light",
      "action": "off"
    }
  }
]


This creates a real automation:

When the garage door opens → turn on the garage light
When it closes → turn it off

🖥️ Dashboard UI

The dashboard provides:

A tile for each device

JSON state display

Color-coded indicators

Lights → green/red buttons

Garage door → OPEN/CLOSED badge

Real-time refresh with no page reload

Powered by Server-Sent Events:

const evt = new EventSource("/events");
evt.onmessage = function(event) { ... }

🧩 Device Definition (devices.json)

Defines each device and its MQTT topics:

"garage_light": {
  "class": "light",
  "topics": {
    "state": "sentinel/garage/light/state",
    "command": "sentinel/garage/light/command"
  }
}


Classes supported out of the box:

garage_door

light

fan

📘 Virtual Device Behavior

All devices share the same pattern:

on_connect → publish initial state

on_message → update state based on commands

heartbeat thread → republish state every second

Garage door uses:

{"position": "open" | "closed"}


Lights + fan use:

{"power": "on" | "off"}

📝 Logging

Hub logs state changes and rule triggers:

logs/hub.log


Example:

2025-01-13 14:22:01 - State change: garage_door_main → {"position": "open"}
2025-01-13 14:22:01 - Rule fired: garage_light ← on


Each virtual device logs to:

logs/<device>.log

📅 Roadmap (Next Planned Steps)

These are the logical next enhancements:

V1.1

Rule dedupe (already implemented)

Quiet-mode for virtual devices (only log on change)

UI polish (icons, animations)

Dark mode toggle

V2

Multi-condition rules

Timers / delays

Scenes (“Evening Mode”)

Real device adapters (ESP32, Zigbee, etc.)

Inbound state requests (MQTT “get” topics)

✔ Current Status

Sentinel is fully functional:

All devices simulate correctly

Hub automation is working

Dashboard is real-time and stable

“Garage door → light on/off” rule works end-to-end

Repo now has structure suitable for expansion

You now have the foundation of a clean, modular home automation engine.

If you want, I can also generate:

CONTRIBUTING.md

CHANGELOG.md

Full API documentation

A “how to write your own device” guide

A versioned milestone roadmap

Just say the word.
