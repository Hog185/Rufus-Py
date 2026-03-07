#due to some issues it's only working with linux don't add without proper changing
import subprocess
import sys
import os 
import shutil

"""
This will install grub with a config that lets you boot into the selected iso
"""

def install_clone(target_device,selected_iso):
    
    # the iso must exist
    if not os.path.exists(selected_iso):
        print(f"Error: Source ISO '{selected_iso}' not found.")
        sys.exit(1)
    
    # target device like /dev/sdX
    #if its an nvme abort immediately
    
    if "nvme" in target_device:
        print(f"Aborting: {target_device} is likely to a system drive.")
        sys.exit(1)
        
        
    # Partitionning system using 3 parts layout for maximum compatibility
    # defining part Using GPT UUIDs for precision
    # part1: BIOS Boot (Type: 21686148...)
    # part2: EFI System (Type: C12A7328...)
    # part3: Data (Type: EBD0A0A2...)
    
    sfdisk_input=f"""
    label: gpt
    device: {target_device}
    unit: sectors
    
{target_device}1 : start=2048, size=2048, type=21686148-6449-6E6F-7444-6961676F6E61
{target_device}2 : start=4096, size=204800, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B
{target_device}3 : start=208896, type=EBD0A0A2-B9E5-4433-87C0-68B6B72699C7
    """
    try:
        print(f"Partitioning {target_device} ... ;)")
        subprocess.run(['sfdisk',target_device],input=sfdisk_input.encode(),check=True)
        
        subprocess.run(["partprobe"], check=False)
        subprocess.run(["udevadm", "settle"], check=False)
        
        print("Formatting partitions ")
        subprocess.run(['mkfs.vfat', '-F', '32', '-n', 'EFI', f"{target_device}2"], check=True)
        subprocess.run(['mkfs.exfat', '-L', 'OS_PART', f"{target_device}3"], check=True)

        # 3. MOUNT EFI & INSTALL GRUB
        efi_mount = "/tmp/efi"
        os.makedirs(efi_mount, exist_ok=True)
        subprocess.run(['mount', '-t', 'vfat', f"{target_device}2", efi_mount], check=True)
        
        
        print("Installing GRUB")
        subprocess.run(['grub-install', '--target=i386-pc', f'--boot-directory={efi_mount}/boot', target_device], check=True)
        subprocess.run(['grub-install', '--target=x86_64-efi', f'--efi-directory={efi_mount}', f'--boot-directory={efi_mount}/boot', '--removable'], check=True)
        # grub config
        config_content = """
insmod part_gpt
insmod exfat
insmod loopback
insmod iso9660
search --no-floppy --label OS_PART --set=root
set timeout=1
menuentry "Start OS" {
    set isofile="/os.iso"
    loopback loop ($root)$isofile
    linux (loop)/casper/vmlinuz boot=casper iso-scan/filename=$isofile quiet splash
    initrd (loop)/casper/initrd
}
"""
        with open(f"{efi_mount}/boot/grub/grub.cfg", "w") as cfg:
            cfg.write(config_content)
        
        subprocess.run(['umount', efi_mount], check=True)

        # 4. MOUNT DATA & COPY ISO
        data_mount = "/tmp/vtoy_data"
        os.makedirs(data_mount, exist_ok=True)
        subprocess.run(['mount', f"{target_device}3", data_mount], check=True)

        print(f"--- Copying {selected_iso} to USB as os.iso ---")
        print("This may take a few minutes...")
        shutil.copy2(selected_iso, f"{data_mount}/os.iso")
        
        # sync ensures the data is actually written nand
        subprocess.run(['sync'], check=True)
        subprocess.run(['umount', data_mount], check=True)

        print("\nSUCCESS: Your single-boot USB is ready.")        
        
        
    except subprocess.CalledProcessError as e:
        print(f"Command failled: {e}")
        sys.exit(1)
        
# this part is for testing the script        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 script.py <target_device> <source_iso>")
    else:
        install_clone(sys.argv[1], sys.argv[2])
