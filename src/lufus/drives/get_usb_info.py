import psutil
import os
import subprocess


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