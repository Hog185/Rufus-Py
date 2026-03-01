# Rufus-PY  
### Work in Progress — Use With Caution

Rufus-PY is a Linux USB imaging tool written in Python. It is inspired by the Windows utility Rufus, but built specifically for Linux systems and workflows.

The goal of this project is simple: provide a straightforward way to write ISO images to USB drives using native Linux tools, while adding basic validation and safety checks to reduce user error.

---

## Overview

Rufus-PY works by interacting directly with standard Linux utilities such as:

- `dd` for disk imaging  
- `lsblk` for device detection  
- `mkfs` tools for formatting  

Instead of abstracting away system behavior, the application acts as a controlled wrapper around these tools. This keeps operations transparent and predictable.

---

## Features

- Automatic detection of mounted USB devices  
- ISO validation using signature checks  
- Removable device verification before writing  
- Raw disk flashing support  
- Formatting options (NTFS, FAT32, exFAT, ext4)  
- Volume label support  
- Quick format option  
- Optional GUI launcher  

---

## Design Approach

The project focuses on:

- Clear, readable Python code  
- Minimal dependencies  
- Direct interaction with the Linux disk system  
- Practical safeguards before destructive operations  

Rufus-PY does not attempt to replace low-level system tools. Instead, it coordinates them in a structured and controlled way.

---

## Project Status

This project is currently a work in progress.

Core functionality is implemented, but the software performs destructive disk operations and should be tested carefully. It is not yet recommended for production or mission-critical environments.

⚠️ Flashing or formatting a device will permanently erase its contents. Always confirm the selected device before proceeding.

---

## Intended Use

Rufus-PY is intended for:

- Linux users who prefer a Python-based solution  
- Developers interested in extending disk utility logic  
- Users who want a lightweight alternative approach  

Contributions, testing, and feedback are welcome as the project continues to evolve.
