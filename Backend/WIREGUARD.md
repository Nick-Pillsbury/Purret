## WireGuard + Purret backend (Raspberry Pi)

WireGuard is an **OS-level VPN**. `Backend/main.py` does not “connect to the Pi” directly; instead:

- WireGuard brings up a network interface (usually `wg0`) on the Pi and on your client machine.
- Your client talks to the FastAPI server using the Pi’s **WireGuard IP** (for example `http://10.7.0.1:8000`).

### Run the API on the Pi

1. Install and configure WireGuard on the Pi (commonly `wg-quick up wg0`).
2. Start the API bound to all interfaces (or specifically the WireGuard interface IP):

```bash
# Example: bind to all interfaces
PURR_BIND_HOST=0.0.0.0 PURR_BIND_PORT=8000 python3 main.py

# Example: bind only to WireGuard IP (replace with your Pi’s WG IP)
PURR_BIND_HOST=10.7.0.1 PURR_BIND_PORT=8000 python3 main.py
```

### Client-side “connection”

On your laptop/desktop:

1. Bring up your WireGuard tunnel.
2. Point your frontend/Unity/network client at the Pi’s WireGuard IP + port.
