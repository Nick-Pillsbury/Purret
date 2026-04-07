import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import servo_control

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello world"}
  

class AxisMoveRequest(BaseModel):
  # Use one of:
  # - angle: absolute target angle in degrees
  # - value: axis input (-1..1) which moves relative by `step`
  angle: float | None = None
  value: float | None = Field(default=None, ge=-1.0, le=1.0)
  step: int = Field(default=5, ge=1, le=30)

def _deadzone() -> float:
  try:
    return max(0.0, min(1.0, float(os.getenv("PURR_SERVO_DEADZONE", "0.2"))))
  except ValueError:
    return 0.2

def _delta_degrees(value: float, step: int) -> float:
  if abs(value) < _deadzone():
    return 0.0
  value = max(-1.0, min(1.0, float(value)))
  degrees = max(1, int(round(step * abs(value))))
  return float(degrees if value > 0 else -degrees)

def _get_target_angle(current: float, request: AxisMoveRequest) -> float:
  if request.angle is not None:
    return float(request.angle)
  if request.value is None:
    raise HTTPException(status_code=400, detail="Provide either 'angle' or 'value'")
  return float(current) + _delta_degrees(float(request.value), request.step)


@app.get("/status")
def status():
  return {
    "ok": True,
    "angles": {
      "servo1": float(getattr(servo_control, "current_angle_servo1", 0.0)),
      "servo2": float(getattr(servo_control, "current_angle_servo2", 0.0)),
    },
  }


@app.post("/servo1/move")
def move_servo1(request: AxisMoveRequest):
  try:
    target = _get_target_angle(getattr(servo_control, "current_angle_servo1", 0.0), request)
    servo_control.servo_move(servo_control.servo1, target)
    return {"ok": True, "angle": float(target)}
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  
  
@app.post("/servo2/move")
def move_servo2(request: AxisMoveRequest):
  try:
    target = _get_target_angle(getattr(servo_control, "current_angle_servo2", 0.0), request)
    servo_control.servo_move(servo_control.servo2, target)
    return {"ok": True, "angle": float(target)}
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  
@app.post("/laser/on")
def turn_laser_on():
  servo_control.led_on()
  return {"status": "ok", "message": "laser turned on"}

@app.post("/laser/off")
def turn_laser_off():
  servo_control.led_off()
  return{"satus": "ok", "message": "laser turned off"}

