# Raspberry Pi Setup Guide

This document outlines the setup process for the Raspberry Pi used in the project.  
This covers the OS choice, installation, Tunnel choice, Wireguard setup, installation Script for necessary dependencies.

---

## Operating System Selection

**Chosen OS:** Raspberry Pi OS Lite (64-bit)

### Rationale
Raspberry Pi OS Lite (64-bit) was selected because:
- Full support for Raspberry Pi hardware (GPIO, I2C, PWM, camera)
- Better compatibility with Pi camera tools (`libcamera`)
- Lower system overhead compared to other variants
- Improved performance and stability for video capture and hardware control
- Suitable for headless operation and Docker-based workloads

The 64-bit version allows full utilization of the Raspberry Pi 5’s 8GB of RAM.

---

## OS Installation

### Required Tools
- Raspberry Pi Imager
- MicroSD card (minimum 16GB recommended)
- MicroSD card reader
- Raspberry Pi 5

### Installation Steps
1. Download and install **Raspberry Pi Imager** from the official Raspberry Pi website.
2. Insert the MicroSD card into your computer.
3. Open Raspberry Pi Imager and select:
   - **Device:** Raspberry Pi 5
   - **Operating System:** Raspberry Pi OS Lite (64-bit)
   - **Storage:** Target MicroSD card
4. Configure OS customization options:
   - Set hostname
   - Enable SSH
   - Configure user and password
   - Set WiFi credentials
5. Write the image to the MicroSD card.
6. Safely insert it into the Raspberry Pi.
7. Power on the Raspberry Pi and verify successful boot.

---

### Verification
- Confirm the system boots successfully
- Verify SSH access
- Confirm OS version using:
```bash 
uname -a
```

## Wireguard Usage


## Wireguard Setup


## Installation Script for Wireguard and Dependencies 