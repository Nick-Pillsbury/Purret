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

# Servo 2 adjustments for different range of movement
servo2.actuation_range = 270
# # Needs new PWM range to accommodate the wider range of movement
servo2.min_pulse = 200
servo2.max_pulse = 2800

# servo2.actuation_range = 180
# servo2.min_pulse = 500
# servo2.max_pulse = 2500


def servo_move(servo, angle):
  if servo == servo2:               
    if angle > 270 or angle < 0: # servo 2 has a different range of movement - this checks if valid angle
      raise ValueError("Invalid angle provided for servo 2")
  else:
    if angle > 180 or 10 > angle: # same angle check for servo 1 with its range of movement
      raise ValueError("Invalid angle provided for servo 1") # servo 1 cannot go below 10 degrees as the bar will get stuck on the base of the structure
  # Sets the angle of the servo to specified value
  servo.angle = angle
  
def both_move(angle1, angle2):
  servo_move(servo1, angle1) #move first servo
  servo_move(servo2, angle2) #move second servo
  
def reset_servos():
  both_move(90, 90) # reset both servos to 90 degree position
  
# reset_servos()

# both_move(0, 0) # move both servos to 0 degree position

# both_move(180, 270) # move both servos to their max angle positions

# servo_move(servo1, 10)

servo_move(servo2, 0)
time.sleep(2)
servo_move(servo2, 180)
