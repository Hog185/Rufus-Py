import psutil
import os
import subprocess
import getpass
import json
import sys
import urllib.parse

##### FUNCTIONS #####
###USB RECOGNITION###
def find_usb():
    usbdict = {}    # DICTIONARY WHERE USB MOUNT PATH IS KEY AND LABEL IS VALUE
    
    # Get current username
    username = getpass.getuser()
    
    # Properly formatted paths with actual username
    paths = ["/media", "/run/media", f"/media/{username}", f"/run/media/{username}"]
    
    # First, collect all possible user directories from media paths
    all_directories = []
    for path in paths:
        if os.path.exists(path) and os.path.isdir(path):
            try:
                directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
                all_directories.extend([os.path.join(path, d) for d in directories])
            except PermissionError:
                print(f"Permission denied accessing {path}")
                continue
            except Exception as err:
                # catching other exceptions makes debugging easier
                print(f"Error accessing {path}: {err}")
                continue
    
    # Check each partition to see if it matches our potential mount points
    for part in psutil.disk_partitions():
        for mount_path in all_directories:
            if part.mountpoint == mount_path:
                device_node = part.device
                if device_node:
                    try:
                        # Get the label of the USB device
                        label = subprocess.check_output(["lsblk", "-d", "-n", "-o", "LABEL", device_node], text=True, timeout=5).strip()
                        if not label:  # If no label, use directory name
                            label = os.path.basename(mount_path)
                        usbdict[mount_path] = label
                        print(f"Found USB: {mount_path} -> {label}")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        # If lsblk fails, use directory name as fallback
                        label = os.path.basename(mount_path)
                        usbdict[mount_path] = label
                        print(f"Found USB: {mount_path} -> {label}")
    
    return usbdict

# Actual functionality
def CheckFileSignature(file_path) -> bool:
    # Check if the file:
    # - exists
    # - is a regular file (not a directory)
    # - has proper "magic numbers" for an ISO file (0x43 0x44 0x30 0x30 at offset 32769)

    # this will make sure user doesn't try to break the program by passing a fake .iso

    if not os.path.isfile(file_path):
        print(f"File does not exist: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            f.seek(32769) # moves offset to where magic numbers should be
            magic = f.read(5) # read 5 bytes to read CD001
            if magic == b'\x43\x44\x30\x30\x31':  # "CD001" in hex (applied)
                print(f"Valid ISO file: {file_path}")
                return True
            else:
                print(f"Invalid ISO file (magic number mismatch): {file_path}")
                return False
    except PermissionError:
        print(f"Permission denied when trying to read file: {file_path}")
        return False
    except Exception as err:
        print(f"Error checking file signature: {err}")
        return False

def _is_removable_device(device_node) -> bool:
    """Check that a device is removable (e.g. USB stick) before writing to it."""
    base_name = os.path.basename(device_node).rstrip("0123456789")
    removable_path = f"/sys/block/{base_name}/removable"
    try:
        with open(removable_path, "r") as f:
            return f.read().strip() == "1"
    except OSError:
        return False


def _resolve_device_node(usb_mount_path) -> str | None:
    """Resolve a mount path to its underlying device node for dd."""
    normalized = os.path.normpath(usb_mount_path)
    for part in psutil.disk_partitions():
        if os.path.normpath(part.mountpoint) == normalized:
            return part.device
    return None


def FlashUSB(iso_path, usb_mount_path) -> bool:
    # Resolve the device node from the mount path — dd must target the
    # raw device (e.g. /dev/sdb), not the mounted directory.
    device_node = _resolve_device_node(usb_mount_path)
    if not device_node:
        print(f"Could not resolve device node for mount path: {usb_mount_path}")
        return False

    # Strip the partition number so dd writes to the whole disk
    raw_device = "/dev/" + os.path.basename(device_node).rstrip("0123456789")

    if not _is_removable_device(raw_device):
        print(f"Aborting: {raw_device} is not a removable device.")
        return False

    dd_args = ["dd", f"if={iso_path}", f"of={raw_device}",
               "bs=4M", "status=progress", "conv=fdatasync"]
    print(f"Flashing USB with command: {' '.join(dd_args)}")

    try:
        if CheckFileSignature(iso_path):
            subprocess.run(dd_args, check=True)
            print(f"Successfully flashed {iso_path} to {raw_device}")
            return True
        else:
            print(f"Aborting flash: {iso_path} is not a valid ISO file.")
            return False
    except PermissionError:
        print(f"Permission denied when trying to flash USB: {raw_device}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error during flashing process: {e}")
        return False
    except Exception as err:
        print(f"Unexpected error during flashing process: {err}")
        return False

def GetUSBInfo(usb_path) -> dict:
    try:
        normalized_usb_path = os.path.normpath(usb_path)

        # Get the device node from the mount path
        partitions = psutil.disk_partitions()
        device_node = None
        for part in partitions:
            if os.path.normpath(part.mountpoint) == normalized_usb_path:
                device_node = part.device
                break

        if not device_node:
            print(f"Could not find device node for USB path: {usb_path}")
            return {}

        # Check if USB size is greater than 32GB
        # Use -b for a reliable integer (bytes) instead of human-readable output
        size_output = subprocess.check_output(
            ["lsblk", "-d", "-n", "-b", "-o", "SIZE", device_node],
            text=True, timeout=5
        ).strip()

        if not size_output.isdigit():
            print(f"Warning: could not parse device size: {size_output!r}")
            usb_size = 0
        else:
            usb_size = int(size_output)
        
        if usb_size > 32 * 1024**3:  # 32GB in bytes
            print(f"USB device is large, does user want to actually flash this?: {usb_size} bytes (passed 32 GB threshold)")
        
        # Get the label of the USB device
        label = subprocess.check_output(["lsblk", "-d", "-n", "-o", "LABEL", device_node], text=True, timeout=5).strip()
        if not label:  # If no label, use directory name
            label = os.path.basename(usb_path)
        
        usb_info = {
            "device_node": device_node,
            "label": label,
            "mount_path": usb_path
        }
        print(f"USB Info: {usb_info}")
        return usb_info
    except PermissionError:
        print(f"Permission denied when trying to get USB info: {usb_path}")
        return {}
    except subprocess.CalledProcessError as e:
        print(f"Error getting USB info: {e}")
        return {}
    except Exception as err:
        print(f"Unexpected error getting USB info: {err}")
        return {}


def launch_gui_with_usb_data() -> None:
    usb_devices = find_usb()
    print("Detected USB devices:", usb_devices)

    usb_json = json.dumps(usb_devices)
    encoded_data = urllib.parse.quote(usb_json)

    try:
        subprocess.run([sys.executable, "gui.py", encoded_data], check=True)
    except FileNotFoundError as e:
        print(f"Failed to launch GUI: executable or script not found: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"GUI exited with an error (return code {e.returncode}): {e}")
        sys.exit(e.returncode or 1)
    except Exception as e:
        print(f"Unexpected error while launching GUI: {e}")
        sys.exit(1)





if __name__ == "__main__":
    launch_gui_with_usb_data()
