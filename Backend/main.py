from __future__ import annotations

import uuid
from typing import Any, Dict, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

app = FastAPI(title="Purret Control API (Skeleton)")

#
# NOTE
# This file is intentionally a minimal skeleton that mirrors `endpoints.md`.
# Every endpoint is `async def` and returns placeholder JSON so you can fill in
# real Docker/hardware commands later.
#


# --- Minimal auth: single-user lock (only one username logged in at a time) ---
security = HTTPBearer()
active_token: str | None = None


def require_session(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    if active_token is None or token != active_token:
        raise HTTPException(status_code=403, detail="Invalid or expired session")
    return token


@app.post("/login")
async def login():
    global active_token
    if active_token is not None:
        raise HTTPException(status_code=403, detail="System already in use")
    token = str(uuid.uuid4())
    active_token = token
    return {"token": token}


@app.post("/logout")
async def logout(_: str = Depends(require_session)):
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
# 1) Front to Master (HTTP)
# - Servo Movement (Up, Down, Left, Right)
# - Camera
# - Laser
# - Power on/off
# - Starting/Stopping containers
# - Passing up errors
# - (record user id and only allow user) -> enforced via require_session
# =============================================================================


@app.post("/front/servo/move")
async def front_servo_move(body: ServoMoveRequest, _: str = Depends(require_session)):
    return {"ok": True, "todo": "send servo move to master/servo service", "body": body.model_dump()}


@app.post("/front/camera/start")
async def front_camera_start(_: str = Depends(require_session)):
    return {"ok": True, "todo": "tell master to start camera"}


@app.post("/front/camera/stop")
async def front_camera_stop(_: str = Depends(require_session)):
    return {"ok": True, "todo": "tell master to stop camera"}


@app.post("/front/camera/record/start")
async def front_camera_record_start(_: str = Depends(require_session)):
    return {"ok": True, "todo": "tell master/camera to start recording"}


@app.post("/front/camera/record/stop")
async def front_camera_record_stop(_: str = Depends(require_session)):
    return {"ok": True, "todo": "tell master/camera to stop recording"}


@app.get("/front/camera/health")
async def front_camera_health(_: str = Depends(require_session)):
    return {"ok": True, "todo": "proxy camera health check"}


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
    return {"ok": True, "todo": "master->camera start"}


@app.post("/camera/stop")
async def camera_stop(_: str = Depends(require_session)):
    return {"ok": True, "todo": "master->camera stop"}


@app.post("/camera/record/start")
async def camera_record_start(_: str = Depends(require_session)):
    return {"ok": True, "todo": "master->camera record start"}


@app.post("/camera/record/stop")
async def camera_record_stop(_: str = Depends(require_session)):
    return {"ok": True, "todo": "master->camera record stop"}


@app.get("/camera/health")
async def camera_health(_: str = Depends(require_session)):
    return {"ok": True, "todo": "master->camera health check"}


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


@app.post("/servo/move")
async def servo_move(body: ServoMoveRequest, _: str = Depends(require_session)):
    return {"ok": True, "todo": "master->servo movement", "body": body.model_dump()}


@app.get("/servo/health")
async def servo_health(_: str = Depends(require_session)):
    return {"ok": True, "todo": "master->servo health check"}


@app.get("/system-status")
async def system_status():
    return {"session_active": active_token is not None}
