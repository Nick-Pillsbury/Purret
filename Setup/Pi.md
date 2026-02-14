# Raspberry Pi Setup Guide

This document outlines the setup process for the Raspberry Pi used in the project.  
This covers the OS choice, installation, Tunnel choice, Wireguard setup, and installation Scripts.

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

### OS Verification
1. Confirm the system boots successfully
2. Verify wifi or lan access
3. Verify SSH access
4. Update and upgrade everything
   ```bash
   sudo apt update
   sudo apt upgrade
   ```
5. Confirm OS version using:
   ```bash 
   uname -a
   ```
6. Confirm Hostname using
   ```bash
   hostname
   ```
7. Add new sudo user if needed
   ```bash
   sudo adduser newusername
   sudo usermod -aG sudo newusername
   ```

---

## Tunnel Choice
WireGuard is used to create a secure, VPN tunnel between the Raspberry Pi / local network and the outside internet. This enables encrypted remote access, secure data transmission, and safe management of the device from external networks. It will allow to connect to the pi from anywhere, while opening the local network to the internet securely.

---

## Manual Wireguard Setup

### Server Setup

1. Enable Ip Forwarding
   ```bash
   sudo nano /etc/sysctl.conf
   Uncomment:
      net.ipv4.ip_forward=1
   sudo sysctl -p
   ```

2. Enable Internet Routing
   ***Use wlan0 for Wifi and eth0 for Lan***
   ```bash
   sudo apt install iptables-persistent -y
   sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
   sudo netfilter-persistent save
   ```
3. Install Wireguard
   ```bash
   sudo apt install wireguard -y
   ```
4. Verify Install
   ```bash
   wg --version
   ```
5. Create Mutiple Pairs of Private and Public Keys
   ```bash
   cd ~
   mkdir keys
   cd keys
   wg genkey | tee -a server_privatekey.txt | wg pubkey >> server_publickey.txt
   for i in {1..5}; do
      wg genkey | tee -a client_privatekeys.txt | wg pubkey >> client_publickeys.txt
   done
   ```
6. Create Wireguard Config File
   ```bash
   sudo nano /etc/wireguard/wg0.conf
   sudo chmod 600 /etc/wireguard/wg0.conf
   ```
   ```conf
   [Interface]
   PrivateKey = <SERVER_PRIVATE_KEY>
   Address = 10.0.0.1/24
   ListenPort = 51820

   # Client 1
   [Peer]
   PublicKey = <CLIENT1_PUBLIC_KEY>
   AllowedIPs = 10.0.0.2/32

   # Client 2
   [Peer]
   PublicKey = <CLIENT2_PUBLIC_KEY>
   AllowedIPs = 10.0.0.3/32

   # Client 3
   [Peer]
   PublicKey = <CLIENT3_PUBLIC_KEY>
   AllowedIPs = 10.0.0.4/32

   # Client 4
   [Peer]
   PublicKey = <CLIENT4_PUBLIC_KEY>
   AllowedIPs = 10.0.0.5/32

   # Client 5
   [Peer]
   PublicKey = <CLIENT5_PUBLIC_KEY>
   AllowedIPs = 10.0.0.6/32
   ```
7. Port Forward on Router
   **On your router port forward a free port to your pi <LOCAL_IP:WG_LISTENING_PORT>**
   This will allow clients to connect to your <PUBLIC_IP>:<ROUTER_PORT> and be forwarded to the wireguard server.

### Client Config Example
```config
[Interface]
PrivateKey = <CLIENT_PRIVATE_KEY>
Address = 10.0.0.X/24
DNS = 1.1.1.1

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <YOUR_PUBLIC_IP>:<ROUTER_PORT>
AllowedIPs = 10.0.0.0/24, 192.168.1.0/24
PersistentKeepalive = 25
```



### Wireguards Commands
   > Start Tunnel
   > ```sudo wg-quick up wg0```
   >
   > Stop Tunnel
   > ```sudo wg-quick down wg0```
   >
   > Enable Startup
   > ```sudo systemctl enable wg-quick@wg0```
   >
   > Disable Startup
   > ```sudo systemctl disable wg-quick@wg0```
   >
   > Check Service Status
   > ```sudo systemctl status wg-quick@wg0```
   >
   > Show Active Tunnel Info
   > ```sudo wg```
   >
   > Show Interface Details
   > ```ip a show wg0```

---

## Installation Scripts
