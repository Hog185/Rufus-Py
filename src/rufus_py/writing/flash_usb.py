import os
import subprocess
from rufus_py.writing.check_file_sig import _resolve_device_node
from rufus_py.writing.check_file_sig import check_iso_signature

def FlashUSB(iso_path, usb_mount_path) -> bool:
    # Resolve the device node from the mount path — dd must target the
    # raw device (e.g. /dev/sdb), not the mounted directory.
    device_node = _resolve_device_node(usb_mount_path)
    if not device_node:
        print(f"Could not resolve device node for mount path: {usb_mount_path}")
        return False

    # Strip the partition number so dd writes to the whole disk
    raw_device = "/dev/" + os.path.basename(device_node).rstrip("0123456789")

    dd_args = ["dd", f"if={iso_path}", f"of={raw_device}",
               "bs=4M", "status=progress", "conv=fdatasync"]
    print(f"Flashing USB with command: {' '.join(dd_args)}")

    try:
        if check_iso_signature(iso_path):
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
