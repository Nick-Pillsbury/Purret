from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid
import asyncio
from typing import Dict
from datetime import datetime

from state_machine import StateMachine, SystemState
from models import ServoCommand, LaserCommand, VideoCommand, LoginRequest

app = FastAPI(title="Purret Control API")


# Global System Components
state_machine = StateMachine()
active_sessions: Dict[str, str] = {}  # token -> username
event_log = []
telemetry_data = {
    "servo_angle": 0,
    "laser_enabled": False,
    "recording": False,
    "temperature": 30.0,
    "battery": 95
}

security = HTTPBearer()


# Utilities
def log_event(message: str):
    event_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "message": message
    })

def verify_session(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in active_sessions:
        raise HTTPException(status_code=403, detail="Invalid or expired session")
    return active_sessions[token]


# Authentication (Single User Enforcement)
@app.post("/login")
async def login(request: LoginRequest):
    if state_machine.current_user:
        raise HTTPException(status_code=403, detail="System already in use")

    token = str(uuid.uuid4())
    active_sessions[token] = request.username
    state_machine.current_user = request.username

    log_event(f"{request.username} logged in")
    return {"token": token}


@app.post("/logout")
async def logout(user: str = Depends(verify_session)):
    token = [k for k, v in active_sessions.items() if v == user][0]
    del active_sessions[token]
    state_machine.current_user = None
    state_machine.state = SystemState.IDLE

    log_event(f"{user} logged out")
    return {"message": "Logged out successfully"}


# Control Endpoints
@app.post("/servo")
async def control_servo(cmd: ServoCommand, user: str = Depends(verify_session)):
    if state_machine.state == SystemState.ERROR:
        raise HTTPException(status_code=400, detail="System in ERROR state")

    telemetry_data["servo_angle"] = cmd.angle
    state_machine.transition(SystemState.ACTIVE)

    log_event(f"{user} set servo to {cmd.angle} degrees")

    await asyncio.sleep(0.2)  # Simulate hardware I/O

    return {"status": "Servo moved", "angle": cmd.angle}

@app.post("/laser")
async def control_laser(cmd: LaserCommand, user: str = Depends(verify_session)):
    telemetry_data["laser_enabled"] = cmd.enabled
    state_machine.transition(SystemState.ACTIVE)

    log_event(f"{user} turned laser {'ON' if cmd.enabled else 'OFF'}")

    return {"laser_enabled": cmd.enabled}

@app.post("/video")
async def control_video(cmd: VideoCommand, user: str = Depends(verify_session)):
    if cmd.action == "start":
        telemetry_data["recording"] = True
        state_machine.transition(SystemState.RECORDING)
        log_event(f"{user} started recording")
    elif cmd.action == "stop":
        telemetry_data["recording"] = False
        state_machine.transition(SystemState.ACTIVE)
        log_event(f"{user} stopped recording")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return {"recording": telemetry_data["recording"]}

@app.get("/telemetry")
async def get_telemetry(user: str = Depends(verify_session)):
    # Simulate changing telemetry
    telemetry_data["temperature"] += 0.1
    telemetry_data["battery"] -= 0.05

    return telemetry_data

@app.get("/logs")
async def get_logs(user: str = Depends(verify_session)):
    return {"events": event_log}

@app.get("/system-status")
async def system_status():
    return {
        "state": state_machine.state,
        "current_user": state_machine.current_user,
        "active_sessions": len(active_sessions)
    }