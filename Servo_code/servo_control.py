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
current_angle_servo1 = 90
current_angle_servo2 = 90

# Servo 2 adjustments for different range of movement
MIN_PULSE = 500
MAX_PULSE = 2500

# ------------------------------------------SERVO MOVEMENT FUNCTIONS-----------------------------------------------------------------------

def raw_pulse(channel, pulse_us):
  tick = int((pulse_us / 20000) * 4096)
  PCA.channels[channel].duty_cycle = tick << 4


def servo_move(servo, angle):
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
    
    
    
def smooth_move(servo, angle, speed):
  if speed > 100 or speed < 1:
    raise ValueError("Invalid speed provided")
  
  if servo == servo1:
    if angle > 180 or 0 > angle: # same angle check for servo 1 with its range of movement
      raise ValueError("Invalid angle provided for servo 1") # servo 1 cannot go below 10 degrees as the bar will get stuck on the base of the structure
    for set_angle in range(current_angle_servo1, angle):
      pulse_us = MIN_PULSE + (set_angle/180) * (MAX_PULSE - MIN_PULSE)
      raw_pulse(0, pulse_us)
      time.sleep(1 - (speed / 100))
      current_angle_servo1 = set_angle
  else: 
    if angle > 270 or angle < 0: # servo 2 has a different range of movement - this checks if valid angle
      raise ValueError("Invalid angle provided for servo 2")
    for set_angle in range(current_angle_servo2, angle):
      pulse_us = MIN_PULSE + (set_angle/270) * (MAX_PULSE - MIN_PULSE)
      raw_pulse(1, pulse_us)
      time.sleep(1 - (speed / 100))
      current_angle_servo2 = set_angle
      
    
def both_move(angle1, angle2):
  servo_move(servo1, angle1) #move first servo
  servo_move(servo2, angle2) #move second servo
  
def reset_servos():
  both_move(90, 90) # reset both servos to 90 degree position
  

# ------------------------------------------LASER MODULE FUNCTIONS-----------------------------------------------------------------------

def led_on():
  led_channel.duty_cycle = 0xFFFF  # full ON

def led_off():
  led_channel.duty_cycle = 0x0000  # OFF

def led_pwm(value):  
  # value: 0.0 → 1.0
  led_channel.duty_cycle = int(value * 0xFFFF)



#-------------------------------------------TEST SERVO CODE-----------------------------------------------------
servo_move(servo1, 180) 
time.sleep(2) 
servo_move(servo1, 0)
time.sleep(2)
servo_move(servo2, 270)
time.sleep(2)
servo_move(servo2, 0)

#-------------------------------------------TEST LASER CODE-------------------------------------------------------
led_on()
time.sleep(1)
led_off()
time.sleep(1)
led_pwm(0.1)  # 50% brightness
time.sleep(1)
led_pwm(1.0)  # full brightness
time.sleep(1)
led_off()

# stops the signal the pca board
PCA.deinit()
