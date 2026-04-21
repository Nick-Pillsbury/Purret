import board
import busio
import time
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
# -------------------------------------GPIO 5 - SCL, GPIO 3 - SDA
i2c = busio.I2C(board.SCL, board.SDA) # Create the I2C (Inter-Integrated Circuit) bus interface. 

PCA = PCA9685(i2c) # creates our driver object - used to control servo
PCA.frequency = 50 # sets teh frequency to 50 Hz PWM - should be good for our servo

#Servo Objects    
servo1 = servo.Servo(PCA.channels[0]) # Servo 1 
servo2 = servo.Servo(PCA.channels[1]) # Servo 2

# Laser Object
led_channel = PCA.channels[2]

#Keep track of current servo angle for smooth movement
current_angle_servo1 = 0
current_angle_servo2 = 0

# SERVO MOVEMENT INCREMENT
ANGLE_INCREMENT = 5 # increment for smooth movement

# Servo 2 adjustments for different range of movement
MIN_PULSE = 500
MAX_PULSE = 2500

DEFAULT_ANGLE_SERVO1 = 90
DEFAULT_ANGLE_SERVO2 = 120

# ------------------------------------------SERVO MOVEMENT FUNCTIONS-----------------------------------------------------------------------

def raw_pulse(channel, pulse_us):
  tick = int((pulse_us / 20000) * 4096)
  PCA.channels[channel].duty_cycle = tick << 4


def servo_move(servo, angle):
  global current_angle_servo1, current_angle_servo2
  if servo == servo1:
    if angle > 180 or 0 > angle: # same angle check for servo 1 with its range of movement
      raise ValueError("Invalid angle provided for servo 1") # servo 1 cannot go below 10 degrees as the bar will get stuck on the base of the structure
    pulse_us = MIN_PULSE + (angle / 180) * (MAX_PULSE - MIN_PULSE ) # calculates the pulse width in microseconds based on the angle
    raw_pulse(0, pulse_us) # sends the pulse to the servo
    current_angle_servo1 = angle # updates the current angle for servo 1
  else: 
    if angle > 270 or angle < 0: # servo 2 has a different range of movement - this checks if valid angle
      raise ValueError("Invalid angle provided for servo 2")
    pulse_us = MIN_PULSE + (angle / 270) * (MAX_PULSE - MIN_PULSE ) # calculates the pulse width in microseconds based on the angle
    raw_pulse(1, pulse_us) # sends the pulse to the servo
    current_angle_servo2 = angle # updates the current angle for servo 2
    
    
def both_move(angle1, angle2):
  servo_move(servo1, angle1) #move first servo
  servo_move(servo2, angle2) #move second servo
  
def reset_servos():
  both_move(DEFAULT_ANGLE_SERVO1, DEFAULT_ANGLE_SERVO2) # reset both servos to face forward
  

def set_defaults(angle1, angle2):
  global DEFAULT_ANGLE_SERVO1, DEFAULT_ANGLE_SERVO2
  if(angle1 > 180 or angle1 < 0):
    raise ValueError("Invalid defualt angle for servo 1")
  if(angle2 > 270 or angle2 < 0):
    raise ValueError("Invalud defualt angle for servo 2")
  DEFAULT_ANGLE_SERVO1 = angle1
  DEFAULT_ANGLE_SERVO2 = angle2


# ------------------------------------------LASER MODULE FUNCTIONS-----------------------------------------------------------------------

def led_on():
  print("turning laser on")
  led_channel.duty_cycle = 0xFFFF  # full ON
  print("laser turned on")

def led_off():
  led_channel.duty_cycle = 0x0000  # OFF

def led_pwm(value):  
  if(value > 1 or value < 0):
    raise ValueError("Invalid value provided for laser brightness")
  # value: 0.0 → 1.0
  led_channel.duty_cycle = int(value * 0xFFFF)


