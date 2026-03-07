import psutil
import hashlib
from pathlib import Path
import os


def _is_valid_sha256_hex(hash_value: str) -> bool:
    normalized = hash_value.strip().lower()
    if len(normalized) != 64:
        return False
    return all(char in "0123456789abcdef" for char in normalized)

def check_iso_signature(file_path: str) -> bool:
    """
    Validate ISO9660 Primary Volume Descriptor at sector 16.
    Offsets:
      32768: volume descriptor type (0x01 for PVD)
      32769-32773: standard identifier 'CD001'
      32774: version (0x01)
    """
    p = Path(file_path)
    if not p.is_file():
        print(f"Error: {file_path} is not a valid file. :(")
        return False

    try:
        with p.open("rb") as f:
            f.seek(32768)
            data = f.read(7)
            if len(data) < 7:
                print(f"Error: {file_path} is too small to contain a valid PVD. :(")
                return False
            
            vd_type, ident, version = data[0], data[1:6], data[6]
            if vd_type == 0x01 and ident == b"CD001" and version == 0x01:
                print(f"Valid ISO file: {file_path}")
                return True
            
            else:
                print(f"Error: {file_path} does not have a valid ISO9660 PVD signature. :(")
                return False
    except OSError as err:
        print(f"Error reading {file_path}: {err} :(")
    

    return False

def _parent_block_device(device_node: str) -> str | None:
    dev_name = os.path.basename(device_node)
    sys_class = Path("/sys/class/block") / dev_name

    try:
        parent_name = sys_class.resolve().parent.name
        if parent_name == dev_name:
            # alr whole disk device
            return device_node
        return f"/dev/{parent_name}"
    except OSError:
        return None


def _resolve_device_node(usb_mount_path: str) -> str | None:
    """Resolve a mount path to its underlying device node for dd."""
    normalized = os.path.normpath(usb_mount_path)
    for part in psutil.disk_partitions(all=True):
        if os.path.normpath(part.mountpoint) == normalized:
            return _parent_block_device(part.device) or part.device
    return None

# sha256 sum checking

def check_sha256(file_path: str, expected_hash: str) -> bool:
    """Check the SHA256 hash of a file against an expected value."""


    # always check if file even exists b4 running anything else, no need to waste time calculating hash if file is not even there
    p = Path(file_path)
    if not p.is_file():
        print(f"Error: {file_path} is not a valid file. :( ")
        return False

    normalized_expected_hash = expected_hash.strip().lower()
    if not _is_valid_sha256_hex(normalized_expected_hash):
        print("Error: expected SHA256 hash must be exactly 64 hexadecimal characters.")
        return False


    sha256 = hashlib.sha256()
    try:
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        calculated_hash = sha256.hexdigest()
        if calculated_hash == normalized_expected_hash:
            print(f"SHA256 hash matches for {file_path}")
            return True
        else:
            print(f"SHA256 hash mismatch for {file_path}: expected {normalized_expected_hash}, got {calculated_hash}")
            print("You should not flash this ISO file, it may be corrupted or tampered with. :(")
            return False
    except OSError as err:
        print(f"Error reading {file_path}: {err} :(")

    return False
# to the person that reads this: may you have a good day <3 
# love, koyo
