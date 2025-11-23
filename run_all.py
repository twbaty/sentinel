import subprocess
import time
import os
import sys
import signal

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE = os.path.dirname(os.path.abspath(__file__))

HUB = os.path.join(BASE, "hub", "hub.py")
GARAGE = os.path.join(BASE, "nodes", "virtual_garage.py")

procs = []


# ---------------------------------------------------------
# Helper to start processes
# ---------------------------------------------------------

def start_process(label, path):
    print(f"[Sentinel] Starting {label} ...")
    p = subprocess.Popen(
        [sys.executable, path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    procs.append((label, p))
    return p


# ---------------------------------------------------------
# Stream logs live
# ---------------------------------------------------------

def stream_output():
    while True:
        for label, p in procs:
            if p.stdout:
                line = p.stdout.readline()
                if line:
                    print(f"[{label}] {line}", end="")
        time.sleep(0.05)


# ---------------------------------------------------------
# Main runner
# ---------------------------------------------------------

def main():
    print("[Sentinel] Launching hub + virtual garage...")

    # Start hub first
    start_process("Hub", HUB)
    time.sleep(1)  # give hub time to connect to MQTT

    # Start virtual garage
    start_process("Garage", GARAGE)

    print("[Sentinel] All services running.")
    print("Press CTRL+C to stop everything.\n")

    try:
        stream_output()
    except KeyboardInterrupt:
        print("\n[Sentinel] Shutting down...")

        for label, p in procs:
            print(f"[Sentinel] Terminating {label} ...")
            p.terminate()

        print("[Sentinel] All processes stopped.")


if __name__ == "__main__":
    main()
