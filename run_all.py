#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent

PROCESS_SPEC = [
    ("Hub", ["python", str(ROOT / "hub" / "hub.py")]),
    ("Dashboard", ["python", str(ROOT / "dashboard" / "app.py")]),
    ("GarageDoor", ["python", str(ROOT / "nodes" / "virtual_garage_door.py")]),
    ("FanMotor", ["python", str(ROOT / "nodes" / "virtual_fan_motor.py")]),
    ("FanLight", ["python", str(ROOT / "nodes" / "virtual_fan_light.py")]),
    ("GarageLight", ["python", str(ROOT / "nodes" / "virtual_garage_light.py")]),
    ("LivingroomLight", ["python", str(ROOT / "nodes" / "virtual_livingroom_light.py")]),
]


def main():
    procs = []

    print("[run_all] Starting Sentinel environment...\n")

    for name, cmd in PROCESS_SPEC:
        try:
            p = subprocess.Popen(cmd, cwd=ROOT)
            procs.append((name, p))
            print(f"[run_all] Launched {name}")
            time.sleep(0.2)
        except Exception as e:
            print(f"[run_all] ERROR launching {name}: {e}")

    print("\n[run_all] All processes running. Press CTRL+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[run_all] Stopping all processes...")
        for name, p in procs:
            try:
                p.terminate()
            except Exception:
                pass
        for name, p in procs:
            try:
                p.wait(timeout=5)
            except Exception:
                pass
        print("[run_all] Shutdown complete.")


if __name__ == "__main__":
    main()
