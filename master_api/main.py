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
from fastapi import FastAPI
from chat import router as chat_router



app = FastAPI(title="Purret Control API")
app.include_router(chat_router)

# To run locally
#
# PURR_BIND_HOST=10.0.0.1 PURR_BIND_PORT=8000 python main.py
#
# curl -X POST http://10.0.0.1:8000/login
# curl -X POST http://10.0.0.1:8000/logout -H "Authorization: Bearer $TOKEN"


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


Direction = Literal[
    "up",
    "down",
    "left",
    "right",
    "up_left",
    "up_right",
    "down_left",
    "down_right",
    "stop",
]


class ServoMoveRequest(BaseModel):
    # Preferred: joystick-style vector from frontend.
    # - x: left (-1) .. right (+1)
    # - y: down (-1) .. up (+1)
    # You can also send `vector: [x, y]` instead of separate fields.
    x: float | None = None
    y: float | None = None
    vector: tuple[float, float] | None = None

    # Back-compat / convenience: discrete direction (8-way + stop).
    direction: Direction | None = None
    step: int = Field(default=5, ge=1, le=30)


class ErrorReport(BaseModel):
    source: str = Field(default="unknown", min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=512)
    severity: Literal["info", "warning", "error"] = "error"
    details: Optional[Dict[str, Any]] = None


class ContainerOptions(BaseModel):
    options: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Servo service proxy
#
# `Backend/servo testing/test.py` is treated as a separate servo service.
# This API proxies requests to it and returns its JSON responses.
# =============================================================================

def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


_DIR_TO_VEC: dict[str, tuple[float, float]] = {
    "up": (0.0, 1.0),
    "down": (0.0, -1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
    "up_left": (-1.0, 1.0),
    "up_right": (1.0, 1.0),
    "down_left": (-1.0, -1.0),
    "down_right": (1.0, -1.0),
    "stop": (0.0, 0.0),
}

global servo1angle, servo2angle
servo1angle = 90
servo2angle = 90

def _servo_service_base_url() -> str:
    return os.getenv("PURR_SERVO_SERVICE_URL", "http://127.0.0.1:8002").rstrip("/")


def _servo_service_timeout_s() -> float:
    try:
        return float(os.getenv("PURR_SERVO_SERVICE_TIMEOUT_S", "5"))
    except ValueError:
        return 5.0


def _servo_service_request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{_servo_service_base_url()}{path}"

    data: bytes | None = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, method=method, data=data)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=_servo_service_timeout_s()) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Servo service error ({exc.code})") from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail="Servo service unreachable") from exc

    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Servo service returned non-JSON") from exc


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
# - (record user id and only allow user) -> enforced via require_session
# =============================================================================

@app.post("front/servo/reset")
async def servo_reset(_: str = Depends(require_session)):
    global servo1angle, servo2angle
    servo1angle = 90.0
    servo2angle = 90.0
    servo1 = _servo_service_request("POST", "/servo1/move", {"angle": servo1angle})
    servo2 = _servo_service_request("POST", "/servo2/move", {"angle": servo2angle})
    return {"ok": True}



@app.post("/front/servo/move")
@app.post("/servo/move")
async def servo_move(body: ServoMoveRequest, _: str = Depends(require_session)):
    global servo1angle, servo2angle

    if body.direction is not None:
        try:
            x, y = _DIR_TO_VEC[body.direction]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid direction") from None
    elif body.vector is not None:
        x, y = float(body.vector[0]), float(body.vector[1])
    else:
        x = float(body.x or 0.0)
        y = float(body.y or 0.0)

    x = _clamp(x, -1.0, 1.0)
    y = _clamp(y, -1.0, 1.0)
    servo1angle += y * body.step
    servo2angle -= x * body.step


    servo1 = _servo_service_request("POST", "/servo1/move", {"angle": servo1angle})
    servo2 = _servo_service_request("POST", "/servo2/move", {"angle": servo2angle})
    return {"ok": True, "servo1": servo1, "servo2": servo2}


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
    resp = _servo_service_request("POST", "/laser/on")
    return {"ok": True, **resp}


@app.post("/front/laser/off")
async def front_laser_off(_: str = Depends(require_session)):
    resp = _servo_service_request("POST", "/laser/off")
    return {"ok": True, **resp}


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


class ServoAxisMoveRequest(BaseModel):
    # For servo1: y (down=-1 .. up=+1)
    # For servo2: x (left=-1 .. right=+1)
    angle: float = Field(..., ge=0.0, le=180.0)


@app.post("/servo1/move")
@app.post("/front/servo1/move")
async def servo1_move(body: ServoAxisMoveRequest, _: str = Depends(require_session)):
    resp = _servo_service_request("POST", "/servo1/move", body.model_dump())
    return {"ok": True, "servo": resp}


@app.post("/servo2/move")
@app.post("/front/servo2/move")
async def servo2_move(body: ServoAxisMoveRequest, _: str = Depends(require_session)):
    resp = _servo_service_request("POST", "/servo2/move", body.model_dump())
    return {"ok": True, "servo": resp}


@app.get("/servo/health")
async def servo_health(_: str = Depends(require_session)):
    return {"ok": True, **_servo_service_request("GET", "/status")}


@app.get("/system-status")
async def system_status():
    return {"session_active": active_token is not None}
