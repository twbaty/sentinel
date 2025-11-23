#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import time
import signal

ROOT = Path(__file__).resolve().parent

def launch(name, path, args=None):
    if args is None:
        args = []

    print(f"[run_all] Launching {name}")

    # Launch each process with its own prefix using bash -c
    return subprocess.Popen(
        ["bash", "-c", f"python {path} {' '.join(args)}"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

def main():
    print("[run_all] Starting Sentinel environment...\n")

    processes = []

    # Hub
    processes.append(
        launch("Hub", ROOT / "hub" / "hub.py")
    )

    # Dashboard WITHOUT auto-reloader
    processes.append(
        launch("Dashboard", ROOT / "dashboard" / "app.py", ["--no-reload"])
    )

    # Nodes
    processes.append(
        launch("GarageDoor", ROOT / "nodes" / "virtual_garage_door.py")
    )
    processes.append(
        launch("FanMotor", ROOT / "nodes" / "virtual_fan_motor.py")
    )
    processes.append(
        launch("FanLight", ROOT / "nodes" / "virtual_fan_light.py")
    )
    processes.append(
        launch("GarageLight", ROOT / "nodes" / "virtual_garage_light.py")
    )
    processes.append(
        launch("LivingroomLight", ROOT / "nodes" / "virtual_livingroom_light.py")
    )

    print("\n[run_all] All processes running. Press CTRL+C to stop.\n")

    try:
        # Keep run_all alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[run_all] Shutting down...")

        for p in processes:
            p.send_signal(signal.SIGINT)
        for p in processes:
            p.wait()

        print("[run_all] Shutdown complete.")

if __name__ == "__main__":
    main()
