from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import uuid
from typing import Any, Dict, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

app = FastAPI(title="Purret Control API (Skeleton)")

#
# NOTE
#
# PURR_BIND_HOST=10.0.0.1 PURR_BIND_PORT=8000 python main.py
#
# curl -X POST http://10.0.0.1:8000/login
# curl -X POST http://10.0.0.1:8000/logout -H "Authorization: Bearer $TOKEN"


# --- Minimal auth: single-user lock (only one username logged in at a time) ---
security = HTTPBearer()
active_token: str | None = None


class LoginRequest(BaseModel):
    username: str = Field(default="default", min_length=1, max_length=64)


def require_session(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    if active_token is None or token != active_token:
        raise HTTPException(status_code=403, detail="Invalid or expired session")
    return token


@app.post("/login")
async def login(body: LoginRequest | None = None):
    global active_token
    if active_token is not None:
        raise HTTPException(status_code=403, detail="System already in use")

    token = str(uuid.uuid4())
    active_token = token
    return {"token": token}


@app.post("/logout")
async def logout(_: None = None):
    global active_token
    active_token = None
    return {"ok": True}


# --- Shared request models used across multiple endpoint groups ---
Direction = Literal["up", "down", "left", "right"]


class ServoMoveRequest(BaseModel):
    direction: Direction
    step: int = Field(default=5, ge=1, le=30)


class ErrorReport(BaseModel):
    source: str = Field(default="unknown", min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=512)
    severity: Literal["info", "warning", "error"] = "error"
    details: Optional[Dict[str, Any]] = None


class ContainerOptions(BaseModel):
    options: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Camera service proxy
#
# `Backend/camera testing/test.py` is treated as a separate camera service.
# This API proxies requests to it and returns its JSON responses.
# =============================================================================

def _camera_service_base_url() -> str:
    # Example: http://127.0.0.1:8001
    return os.getenv("PURR_CAMERA_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")


def _camera_service_timeout_s() -> float:
    try:
        return float(os.getenv("PURR_CAMERA_SERVICE_TIMEOUT_S", "5"))
    except ValueError:
        return 5.0


def _camera_service_request(method: str, path: str) -> dict[str, Any]:
    url = f"{_camera_service_base_url()}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=_camera_service_timeout_s()) as resp:
            payload = resp.read()
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", "ignore")
        except Exception:
            body = ""
        raise HTTPException(status_code=502, detail=f"Camera service error ({exc.code})") from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail="Camera service unreachable") from exc

    if not payload:
        return {}
    try:
        return json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Camera service returned non-JSON") from exc


# =============================================================================
# 1) Front to Master (HTTP)
# - Servo Movement (Up, Down, Left, Right)
# - Camera
# - Laser
# - Power on/off
# - Starting/Stopping containers
# - Passing up errors
# - (record user id and only allow user) -> enforced via require_session
# =============================================================================


@app.post("/front/servo/move/{direction}")
async def front_servo_move(direction: str, body: ServoMoveRequest, _: str = Depends(require_session)):
    return {"ok": True, "todo": "send servo move to master/servo service", "body": body.model_dump()}


@app.post("/front/camera/start")
async def front_camera_start(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("POST", "/stream/start")}


@app.post("/front/camera/stop")
async def front_camera_stop(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("POST", "/stream/stop")}


@app.post("/front/camera/record/start")
async def front_camera_record_start(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("POST", "/recording/start")}


@app.post("/front/camera/record/stop")
async def front_camera_record_stop(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("POST", "/recording/stop")}


@app.get("/front/camera/health")
async def front_camera_health(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("GET", "/status")}


@app.post("/front/laser/on")
async def front_laser_on(_: str = Depends(require_session)):
    return {"ok": True, "todo": "turn laser on"}


@app.post("/front/laser/off")
async def front_laser_off(_: str = Depends(require_session)):
    return {"ok": True, "todo": "turn laser off"}


@app.post("/front/power/on")
async def front_power_on(_: str = Depends(require_session)):
    return {"ok": True, "todo": "power on system"}


@app.post("/front/power/off")
async def front_power_off(_: str = Depends(require_session)):
    return {"ok": True, "todo": "power off system"}


@app.post("/front/containers/{name}/start")
async def front_container_start(
    name: str, body: ContainerOptions | None = None, _: str = Depends(require_session)
):
    return {"ok": True, "todo": "start docker container", "name": name, "options": (body.options if body else {})}


@app.post("/front/containers/{name}/stop")
async def front_container_stop(
    name: str, body: ContainerOptions | None = None, _: str = Depends(require_session)
):
    return {"ok": True, "todo": "stop docker container", "name": name, "options": (body.options if body else {})}


@app.post("/front/containers/{name}/restart")
async def front_container_restart(
    name: str, body: ContainerOptions | None = None, _: str = Depends(require_session)
):
    return {"ok": True, "todo": "restart docker container", "name": name, "options": (body.options if body else {})}


@app.post("/front/errors")
async def front_report_error(body: ErrorReport, _: str = Depends(require_session)):
    return {"ok": True, "todo": "persist/forward errors", "error": body.model_dump()}


# =============================================================================
# 2) Master to Camera
# - start/stop
# - record
# - health check request
# =============================================================================


@app.post("/camera/start")
async def camera_start(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("POST", "/stream/start")}


@app.post("/camera/stop")
async def camera_stop(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("POST", "/stream/stop")}


@app.post("/camera/record/start")
async def camera_record_start(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("POST", "/recording/start")}


@app.post("/camera/record/stop")
async def camera_record_stop(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("POST", "/recording/stop")}


@app.get("/camera/health")
async def camera_health(_: str = Depends(require_session)):
    return {"ok": True, **_camera_service_request("GET", "/status")}


# =============================================================================
# 3) Master to Servo
# - movement
# - start/stop
# - health check
# =============================================================================


@app.post("/servo/start")
async def servo_start(_: str = Depends(require_session)):
    return {"ok": True, "todo": "master->servo start"}


@app.post("/servo/stop")
async def servo_stop(_: str = Depends(require_session)):
    return {"ok": True, "todo": "master->servo stop"}


@app.post("/servo/move/{direction}")
async def servo_move(direction: str, body: ServoMoveRequest, _: str = Depends(require_session)):
    return {"ok": True, "todo": "master->servo movement", "direction": direction, "body": body.model_dump()}


@app.get("/servo/health")
async def servo_health(_: str = Depends(require_session)):
    return {"ok": True, "todo": "master->servo health check"}


@app.get("/system-status")
async def system_status():
    return {"session_active": active_token is not None}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("PURR_BIND_HOST", "0.0.0.0")
    port = int(os.getenv("PURR_BIND_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False, proxy_headers=True)
