from __future__ import annotations

import ipaddress
import os
import platform
import re
import subprocess
from typing import Any, Iterable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip() in {"1", "true", "True", "yes", "YES"}


def _parse_cidrs(value: str) -> list[ipaddress._BaseNetwork]:
    parts = [p.strip() for p in value.split(",")]
    return [ipaddress.ip_network(p, strict=False) for p in parts if p]


def _client_ip(request: Request) -> ipaddress._BaseAddress | None:
    if not request.client or not request.client.host:
        return None
    try:
        return ipaddress.ip_address(request.client.host)
    except ValueError:
        return None


class SourceIPAllowlistMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        *,
        allowed_networks: Iterable[ipaddress._BaseNetwork],
    ):
        super().__init__(app)
        self._allowed_networks = list(allowed_networks)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        client_ip = _client_ip(request)
        if client_ip is None:
            return JSONResponse(status_code=403, content={"detail": "Client IP not available"})
        if not any(client_ip in network for network in self._allowed_networks):
            return JSONResponse(status_code=403, content={"detail": "Forbidden (source IP not allowed)"})
        return await call_next(request)


def configure_wireguard_allowlist(app: Any) -> None:
    """
    Optional request filter. If enabled, only WireGuard (or other private subnet)
    clients can call the API.

    Env:
      - PURR_WIREGUARD_ONLY=1
      - PURR_ALLOWED_CIDRS=10.0.0.0/24
    """
    if not _env_flag("PURR_WIREGUARD_ONLY"):
        return

    allowed = os.getenv("PURR_ALLOWED_CIDRS", "").strip() or "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,fd00::/8"
    app.add_middleware(SourceIPAllowlistMiddleware, allowed_networks=_parse_cidrs(allowed))


def wireguard_interface_has_ip(interface: str, required_cidr: str | None) -> bool:
    if platform.system().lower() != "linux":
        return True

    try:
        proc = subprocess.run(["ip", "-o", "addr", "show", "dev", interface], capture_output=True, text=True)
    except Exception:  # pragma: no cover (platform/tooling)
        return False

    if proc.returncode != 0:
        return False

    required_network = ipaddress.ip_network(required_cidr, strict=False) if required_cidr else None
    # Example: "4: wg0    inet 10.0.0.1/24 brd 10.0.0.255 scope global wg0"
    for line in proc.stdout.splitlines():
        match = re.search(r"\binet6?\s+([0-9a-fA-F:.]+)/\d+\b", line)
        if not match:
            continue
        try:
            ip = ipaddress.ip_address(match.group(1))
        except ValueError:
            continue
        if required_network is None or ip in required_network:
            return True
    return False


def require_wireguard_or_raise() -> None:
    """
    Optional startup safety check to ensure the WG interface is up.

    Env:
      - PURR_REQUIRE_WIREGUARD=1
      - PURR_WIREGUARD_INTERFACE=wg0
      - PURR_WIREGUARD_CIDR=10.0.0.0/24   (optional)
    """
    if not _env_flag("PURR_REQUIRE_WIREGUARD"):
        return

    interface = os.getenv("PURR_WIREGUARD_INTERFACE", "wg0").strip() or "wg0"
    required_cidr = os.getenv("PURR_WIREGUARD_CIDR", "").strip() or None
    if not wireguard_interface_has_ip(interface, required_cidr):
        detail = f"WireGuard interface '{interface}' is not up"
        if required_cidr:
            detail += f" (expected an IP in {required_cidr})"
        raise RuntimeError(detail)
