Sentinel
Modular MQTT-Driven Home Automation Sandbox
Site: http://localhost:5050/

Sentinel is a lightweight, event-driven home-automation simulator built on:

MQTT messaging

A centralized Hub + automation engine

Virtual device nodes

A real-time Flask dashboard (SSE)

A file-based state & rules model

It’s designed as a learning and experimentation platform for IoT, distributed systems, and automation logic.

📂 Project Structure
sentinel/
│
├── hub/
│   ├── hub.py            # Rules engine + state manager
│   ├── devices.json      # All device metadata + MQTT topics
│   ├── state.json        # Last-known state for every device
│   └── rules.json        # Automation logic (if/then rules)
│
├── dashboard/
│   ├── app.py            # Flask UI + SSE event stream
│   └── templates/
│       └── index.html
│
├── nodes/
│   ├── virtual_garage_door.py
│   ├── virtual_garage_light.py
│   ├── virtual_livingroom_light.py
│   ├── virtual_fan_motor.py
│   └── virtual_fan_light.py
│
├── run_all.py            # Launches hub + dashboard + all nodes
└── README.md

🚀 Running Sentinel

Start everything:

python run_all.py


This launches:

MQTT broker connection

Hub (rules + state)

Dashboard (via Flask)

All virtual devices

Automatic heartbeat threads

Access the UI:

http://127.0.0.1:5050

📡 How Sentinel Works

Sentinel is event-driven:

Device → MQTT → Hub → Rules Engine → MQTT → Device → Dashboard (SSE)

1. Virtual Devices

Each virtual device:

publishes state on connect

republishes every 1 second (heartbeat)

listens for commands

updates internal state when commands arrive

2. Hub

The Hub:

subscribes to sentinel/#

writes every state update to state.json

evaluates rules in rules.json

publishes actions for rules that match

3. Dashboard

The Dashboard:

loads state.json initially

listens live via Server-Sent Events (/events)

updates tiles instantly (no refresh)

changes button colors and door indicators based on state

🧠 Automation Rules

Rules live in hub/rules.json.

Example (garage door → light automation):

[
  {
    "if": {
      "topic": "sentinel/garage/main_door/state",
      "equals": { "position": "open" }
    },
    "then": {
      "device": "garage_light",
      "action": "on"
    }
  },
  {
    "if": {
      "topic": "sentinel/garage/main_door/state",
      "equals": { "position": "closed" }
    },
    "then": {
      "device": "garage_light",
      "action": "off"
    }
  }
]


Rules fire only when state changes.

📘 Device Definitions (devices.json)

Each device specifies:

class (garage_door, light, fan)

its state topic

its command topic

Example:

"garage_light": {
  "class": "light",
  "topics": {
    "state": "sentinel/garage/light/state",
    "command": "sentinel/garage/light/command"
  }
}

🖥️ Dashboard Features

Tile layout (fixed-sized boxes)

Real-time updates via SSE

JSON state viewer

ON/OFF or OPEN/CLOSED buttons

Buttons change color based on device state

Garage door includes a visual status badge

Zero page reloads

📝 Logging

Logs live under:

logs/
│
├── hub.log
└── devices/
    ├── garage_door_main.log
    ├── garage_light.log
    ├── livingroom_light.log
    ├── livingroom_fan_motor.log
    └── livingroom_fan_light.log


Hub logs:

every state update (only on change)

every rule trigger

command actions issued

Devices log:

commands received

state transitions

connection events

📅 Roadmap
V1.1 – Short-Term

UI polish (icons, spacing, animations)

Dark mode

Better tile styling

State validity indicators

Clean logging toggle

V2 – Medium-Term

Multi-condition rules

Delayed actions / timers

“Scenes” (multi-device macros)

Device adapters for real hardware

Request-response support (MQTT “get” topics)

✔ Current Status (Milestone Snapshot)

As of this commit:

All device state flows are stable

Rules engine works (garage door → garage light verified)

Dashboard updates live via SSE

No page flicker

State changes color UI indicators function correctly

Device heartbeat + auto-publish working

Logging quieted (state-change only)

System is now stable enough to pause development and resume later without losing context.

If you want this:

reformatted into separate docs (CONTRIBUTING.md, ARCHITECTURE.md, etc.),

turned into a GitHub Pages site,

or broken into versioned milestones,

I can generate them.
