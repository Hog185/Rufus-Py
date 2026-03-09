import shutil
import sys
import os

def get_install_command(missing_list):
    """Detects the package manager and returns the correct install command."""
    # Mapping our command names to package names for different distros
    pkg_map = {
        "debian": {
            "sfdisk": "util-linux", "mkfs.vfat": "dosfstools", 
            "mkfs.exfat": "exfatprogs", "grub-install": "grub-pc-bin grub-efi-amd64-bin",
            "partprobe": "parted",
            "7z": "p7zip-full"
        },
        "arch": {
            "sfdisk": "util-linux", "mkfs.vfat": "dosfstools", 
            "mkfs.exfat": "exfatprogs", "grub-install": "grub",
            "partprobe": "parted",
            "7z": "p7zip"
        },
        "fedora": {
            "sfdisk": "util-linux", "mkfs.vfat": "dosfstools", 
            "mkfs.exfat": "exfatprogs", "grub-install": "grub2-pc-modules grub2-efi-x64-modules",
            "partprobe": "parted",
            "7z": "p7zip p7zip-plugins"
        }
    }

    # Detect Package MAnager
    if os.path.exists("/usr/bin/apt"):
        manager, distro = "sudo apt install", "debian"
    elif os.path.exists("/usr/bin/pacman"):
        manager, distro = "sudo pacman -S", "arch"
    elif os.path.exists("/usr/bin/dnf"):
        manager, distro = "sudo dnf install", "fedora"
    else:
        return "Please install the missing tools using your system package manager."

    # Unique packages to install
    to_install = set()
    for cmd in missing_list:
        to_install.add(pkg_map[distro].get(cmd, cmd))
    
    return f"{manager} {' '.join(to_install)}"

def verify_system():
    if os.geteuid() != 0:
        print("ERROR: Run as root (sudo).")
        sys.exit(1)

    dependencies = ['sfdisk', 'mkfs.vfat', 'mkfs.exfat', 'grub-install', 'partprobe']
    missing = [cmd for cmd in dependencies if shutil.which(cmd) is None]
    
    if missing:
        print(f"Missing: {', '.join(missing)}")
        print(f"\nRun this to fix:\n{get_install_command(missing)}")
        sys.exit(1)


