import subprocess
import sys
import time
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Process definitions: name, path to script
PROCESSES = [
    ("Hub", ROOT / "hub" / "hub.py"),
    ("Dashboard", ROOT / "dashboard" / "app.py"),
    ("GarageDoor", ROOT / "nodes" / "virtual_garage_door.py"),
    ("FanMotor", ROOT / "nodes" / "virtual_fan_motor.py"),
    ("FanLight", ROOT / "nodes" / "virtual_fan_light.py"),
]

# Colors for output (for readability)
COLORS = [
    "\033[92m",  # Green
    "\033[94m",  # Blue
    "\033[93m",  # Yellow
    "\033[96m",  # Cyan
    "\033[95m",  # Magenta
]
RESET = "\033[0m"


def spawn_process(name, script_path, color):
    """
    Launch script in unbuffered mode so logs appear live.
    """
    return subprocess.Popen(
        [sys.executable, "-u", str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    ), name, color


def main():
    print("[run_all] Starting Sentinel environment...\n")

    processes = []

    # Start each process
    for i, (name, script) in enumerate(PROCESSES):
        if not script.exists():
            print(f"[run_all] ERROR: {script} not found")
            continue

        color = COLORS[i % len(COLORS)]
        proc_tuple = spawn_process(name, script, color)
        processes.append(proc_tuple)
        print(f"[run_all] Launched {name}")

    print("\n[run_all] All processes running. Press CTRL+C to stop.\n")

    try:
        # Continuous output merging
        while True:
            for proc, name, color in processes:
                line = proc.stdout.readline()
                if line:
                    print(f"{color}[{name}] {line.rstrip()}{RESET}")
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\n[run_all] Shutting down processes...")
        for proc, name, _ in processes:
            proc.terminate()
        print("[run_all] All stopped.")


if __name__ == "__main__":
    main()
