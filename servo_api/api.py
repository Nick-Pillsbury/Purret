from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from servo_control import servo_move, reset_servos, set_defaults, servo1, servo2
from servo_control import led_on, led_off, led_pwm

app = FastAPI()
  
class MoveRequest(BaseModel):
    angle: float

class SetDefaultsRequest(BaseModel): 
    angle1: float
    angle2: float

@app.post("/servo1/move")
def move_servo1(request: MoveRequest):
  try:
    servo_move(servo1, request.angle)
    return {"status": "ok", "angle": request.angle}
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  
@app.post("/servo2/move")
def move_servo2(request: MoveRequest):
  try:
    servo_move(servo2, request.angle)
    return {"status": "ok", "angle": request.angle}
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))

@app.post("/servos/set_angles")
def set_defaults(request: SetDefaultsRequest):
  try:
    set_defaults()
    return{"status": "ok", "default angle 1": request.angle1, "default angle 2": request.angle2}
  except ValueError as e:
    raise HTTPException(status_code = 400, detail=str(e))

@app.post("/servos/reset")
def reset_servos():
  try:
    reset_servos()
    return {"status": "ok", "message": "servos reset to default positions"}
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))

class BrightnessRequest(BaseModel):
    value : float # 0.0 - 1.0

@app.post("/laser/pwm")
def set_laser_strength(request: BrightnessRequest):
  try: 
    led_pwm(request.value)
    return  {"status": "ok", "brightness": request.value}
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))

@app.post("/laser/on")
def turn_laser_on():
  led_on() 
  return {"status": "ok", "message": "laser turned on"}

@app.post("/laser/off")
def turn_laser_off():
  led_off()
  return{"satus": "ok", "message": "laser turned off"}