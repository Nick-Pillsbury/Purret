import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
# -------------------------------------GPIO 5 - SCL, GPIO 3 - SDA
i2c = busio.I2C(board.SCL, board.SDA) # Create the I2C (Inter-Integrated Circuit) bus interface. 

PCA = PCA9685(i2c) # creates our driver object - used to control servo
PCA.frequency = 50 # sets teh frequency to 50 Hz PWM - should be good for our servo

#Servo Objects    
servo1 = servo.Servo(PCA.channels[0]) # Servo 1
servo2 = servo.Servo(PCA.channels[1]) # Servo 2


def servo_move(servo, angle):
  # Check if valid angle 0 - 180 degree
  if angle > 180 or 0 > angle:
    raise ValueError("Invalid angle provided")
  servo.angle = angle
  
def both_move(angle1, angle2):
  servo_move(servo1, angle1) #move first servo
  servo_move(servo2, angle2) #move second servo
  
def reset_servos():
  both_move(90, 90) # reset both servos to 90 degree position
  
reset_servos()

both_move(0, 180) # move servo 1 to 0 degree and servo 2 to 180 degree