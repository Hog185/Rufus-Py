import subprocess
import json
import sys
import os
import urllib.parse
from pathlib import Path
from lufus.drives.find_usb import find_usb
import site

def ensure_root():
    # this function checks for x11 or wayland and asks for root perms
    # it also fixes any display issues that might happen due to wrong perm management 
    if os.geteuid() != 0:
        print("Need admin rights. Spawning pkexec...")
        gui_env = {
            "DISPLAY": os.environ.get("DISPLAY"),
            "XAUTHORITY": os.environ.get("XAUTHORITY") or os.path.expanduser("~/.Xauthority"),
            "WAYLAND_DISPLAY": os.environ.get("WAYLAND_DISPLAY"),
            "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR"),
            # THIS IS THE FIX: Pass the current PATH so Bedrock can find all strata commands
            "PATH": os.environ.get("PATH"),
            "PYTHONPATH": os.environ.get("PYTHONPATH", "")
        }
        env_args = ["env"]
        for key, value in gui_env.items():
            if value:
                env_args.append(f"{key}={value}")
        cmd = ["pkexec"] + env_args + [sys.executable] + sys.argv
        os.execvp("pkexec", cmd)

def launch_gui_with_usb_data() -> None:
    ensure_root()
    usb_devices = find_usb()
    print("Detected USB devices:", usb_devices)
    usb_json = json.dumps(usb_devices)
    encoded_data = urllib.parse.quote(usb_json)

    try:
        # START WITH ROOT PERMS
        gui_path = Path(__file__).resolve().with_name("gui.py")
        subprocess.run([sys.executable, str(gui_path), encoded_data], check=True)
    except FileNotFoundError as e:
        print(f"Failed to launch GUI: executable or script not found: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"GUI exited with an error (return code {e.returncode}): {e}")
        sys.exit(e.returncode or e)
    except Exception as e:
        print(f"Unexpected error while launching GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    launch_gui_with_usb_data()
