import subprocess
import os
import glob


def run(cmd):
    subprocess.run(cmd, check=True)


def run_out(cmd) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def _get_wim_size(data_mount) -> int:
    """Check actual install.wim/install.esd size"""
    for pattern in ["install.wim", "install.esd", "INSTALL.WIM", "INSTALL.ESD"]:
        matches = glob.glob(f"{data_mount}/sources/{pattern}")
        if matches:
            return os.path.getsize(matches[0])
    return 0


def _split_wim(data_mount):
    """Split install.wim into 3.8GB chunks for FAT32 compatibility"""
    wim = None
    for pattern in ["install.wim", "INSTALL.WIM"]:
        matches = glob.glob(f"{data_mount}/sources/{pattern}")
        if matches:
            wim = matches[0]
            break

    if not wim:
        print("No install.wim found to split")
        return

    print("Splitting install.wim for FAT32 (file > 4GB)...")
    swm_out = os.path.join(os.path.dirname(wim), "install.swm")
    run(["sudo", "wimlib-imagex", "split", wim, swm_out, "3800"])
    run(["sudo", "rm", wim])
    print("Split complete")


def flash_windows(device, iso, progress_cb=None, status_cb=None):
    def _emit(pct):
        if progress_cb:
            progress_cb(pct)

    def _status(msg):
        print(msg)
        if status_cb:
            status_cb(msg)

    _status("Wiping partition table...")
    run(["sudo", "wipefs", "-a", device])
    _emit(8)

    sfdisk_script = f"""label: gpt
device: {device}
{device}1 : size=512M, type=U
{device}2 : type=EBD0A0A2-B9E5-4433-87C0-68B6B72699C7
"""
    _status("Writing partition table...")
    subprocess.run(["sudo", "sfdisk", device], input=sfdisk_script.encode(), check=True)
    run(["sudo", "partprobe", device])
    run(["sudo", "udevadm", "settle"])
    _emit(15)

    efi  = f"{device}1"
    data = f"{device}2"

    _status("Formatting EFI partition (FAT32)...")
    run(["sudo", "mkfs.vfat", "-F32", "-n", "BOOT", efi])
    _status("Formatting data partition (NTFS)...")
    run(["sudo", "mkfs.ntfs", "-f", "-L", "WINDOWS", data])
    _emit(22)

    run(["sudo", "mkdir", "-p", "/tmp/lufus_efi"])
    run(["sudo", "mkdir", "-p", "/tmp/lufus_data"])
    run(["sudo", "mount", efi, "/tmp/lufus_efi"])
    run(["sudo", "mount", data, "/tmp/lufus_data"])

    try:
        _status("Extracting ISO contents...")
        run(["sudo", "7z", "x", iso, "-o/tmp/lufus_data", "-y"])
        _emit(75)

        wim_size = _get_wim_size("/tmp/lufus_data")
        print(f"install.wim size: {wim_size / (1024**3):.2f} GB")

        _status("Copying EFI boot files...")

        for efi_dir in ["efi", "EFI"]:
            src = f"/tmp/lufus_data/{efi_dir}"
            if os.path.exists(src):
                run(["sudo", "cp", "-r", src, "/tmp/lufus_efi/"])
                print(f"Copied {efi_dir}/ to EFI partition")
                break
        else:
            print("WARNING: No EFI directory found — may not be UEFI bootable")

        for boot_dir in ["boot", "BOOT"]:
            src = f"/tmp/lufus_data/{boot_dir}"
            if os.path.exists(src):
                run(["sudo", "cp", "-r", src, "/tmp/lufus_efi/"])
                print(f"Copied {boot_dir}/ to EFI partition")
                break

        for f in ["bootmgr", "bootmgr.efi"]:
            src = _find_path_case_insensitive("/tmp/lufus_data", f)
            if src:
                run(["sudo", "cp", src, f"/tmp/lufus_efi/{f}"])
                print(f"Copied {f} to EFI partition root")

        _fix_efi_bootloader("/tmp/lufus_efi")
        _emit(88)

        if wim_size > 4 * 1024**3:
            _status("Splitting install.wim for FAT32...")
            _split_wim("/tmp/lufus_data")

        _status("Syncing to disk...")
        run(["sudo", "sync"])
        _emit(97)
    finally:
        run(["sudo", "umount", "/tmp/lufus_efi"])
        run(["sudo", "umount", "/tmp/lufus_data"])

    print("Windows USB ready")
    return True


def _find_path_case_insensitive(base, *parts):
    current = [base]
    for part in parts:
        next_level = []
        for c in current:
            next_level += [
                p for p in glob.glob(os.path.join(c, "*"))
                if os.path.basename(p).lower() == part.lower()
            ]
        current = next_level
    return current[0] if current else None


def _fix_efi_bootloader(efi_mount):
    """
    Ensure /EFI/BOOT/BOOTX64.EFI exists — required by UEFI spec.
    Windows ISOs put the bootloader at efi/microsoft/boot/efisys.bin
    but UEFI firmware looks for /EFI/BOOT/BOOTX64.EFI as fallback.
    """
    found_boot_dir = _find_path_case_insensitive(efi_mount, "EFI", "BOOT")
    boot_dir = found_boot_dir or os.path.join(efi_mount, "EFI", "BOOT")

    existing_bootx64 = _find_path_case_insensitive(efi_mount, "EFI", "BOOT", "BOOTX64.EFI")
    if existing_bootx64:
        print("BOOTX64.EFI already in place")
        return

    bootx64 = os.path.join(boot_dir, "BOOTX64.EFI")
    run(["sudo", "mkdir", "-p", boot_dir])

    src = _find_path_case_insensitive(efi_mount, "EFI", "Microsoft", "Boot", "bootmgfw.efi")
    if src:
        run(["sudo", "cp", src, bootx64])
        print(f"Copied {src} -> {bootx64}")
        return

    print("WARNING: Could not find bootmgfw.efi — UEFI boot may fail")