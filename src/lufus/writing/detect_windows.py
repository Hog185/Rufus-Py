import subprocess
#py7zr doesn't work with cd images but 7z cli tools does

def is_windows_iso(iso_path: str) -> bool:

    try:
        result = subprocess.run(
            ["7z", "l", iso_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            files = result.stdout.lower()
            if any(marker in files for marker in [
                "sources/install.wim",
                "sources/install.esd",
                "sources\\install.wim",   
                "sources\\install.esd",
            ]):
                print("Windows ISO detected via 7z")
                return True
    except FileNotFoundError:
        print("7z not found — install p7zip-full: sudo apt install p7zip-full")
    except subprocess.TimeoutExpired:
        print("7z timed out listing ISO")
    except Exception as e:
        print(f"7z error: {e}")

    try:
        result = subprocess.run(
            ["sudo","blkid", "-o", "value", "-s", "LABEL", iso_path],
            capture_output=True, text=True, timeout=10
        )
        label = result.stdout.strip().upper()
        if "WIN" in label or "WINDOWS" in label:
            print(f"Windows ISO detected via volume label: {label}")
            return True
    except Exception as e:
        print(f"blkid error: {e}")

    return False
