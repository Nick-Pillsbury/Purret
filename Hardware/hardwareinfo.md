
# **HARDWARE DOCUMENTATION**


# Yahboom 2-DOF Servo Pan-Tilt Kit for DIY Robot
* Contents:
  * Contains 2 different servos with different degrees of motion
  * aluminum alloy bracket


## Servo 270
* 20kg metal servo
* 0-270 degrees of motion
* requires 6-7.4 V  otherwise abnormal driving caused


## Servo 180
* 25kg metal servo
* 0-180 degrees of motion
* unknown requirement of voltages

Pulses are used to determine the servo rotation angle:

0.5ms--------------------0°
1.0ms--------------------45°
1.5ms--------------------90°
2.0ms--------------------135°
2.5ms--------------------180°

## Voltages

The original plan was to utilize a 5 volt cable to power the entire apparatus. However atleast one of the servos used requires a higher range of voltage. As a result I have chosen a new power supply for us to utilize that will allow us to control the voltage for our desired output and motor function.

# Servo Driver Module

*  PCA9685 model
   * 16 channels
	 * 12-Bit

# Raspberry Pi connection to board 
---
* a raspberry pi will be used to control the machine via c++ code via custom made API

* Servo Motors will be connected to PCA9685 driver module(s) that is controlled by the Pi

## Notes on wiring the PI

Details involve both servo & pi connection w/out driver from company github:

* Connect Red Wire/positve pole of the servo to the positive pole of the 7.4 V battery _(Will use power supply instead)_
* Connect Brown wire/negative pole of the servo to the negative pole of the 7.4V battery _(Will have be replaced by power supply)_

* Yellow wire (signal wire) of the servo to the physical pin of the Raspberry Pi motherboard (PIN 33) _Refer to Raspberry PI pin diagrams to find the correct pin/ get other info_
  * Also connect gnd connections of motherboard to negative pole of the battery _(Power supply)_


Hardware links:

Servo + Chasis link:https://www.amazon.com/Yahboom-Pan-Tilt-Electric-Platform-Accessories/dp/B0BRXVFCKX?crid=1KUA94PMKSRNO&dib=eyJ2IjoiMSJ9.4eRj_T_iKB1iEngaI6jnfJyJxbKsjoufnNVZFRyi1wvmFuLVeCjG1crIbCtV4qV_Y2q2idksGWQ4dGIFJAHrKKJs3T0r20CkxQ1MvpJ3eno9QmKXwtYMGmKZ60oL7nEpoNH9ie2h_mca1alu6guQEtnNRdajE8VjiVAnYdO9Pc6l2AlqHIIH8AG4n6YPl8J5mSiWRtZAtzuNcqBhQAh63FD5L5aFAt3igRSxgD0a9q8.bxeCgEPO_uW3jdD5FFCNyGg5er72vM_CAFR3qP1aQDM&dib_tag=se&keywords=pan+and+tilt+servo+kit+pi5&qid=1769168785&sprefix=pan+and+tilt+servo+kit+pi5%2Caps%2C189&sr=8-1 

company github page:https://github.com/YahboomTechnology/2DOF-PTZ 


Driver link:
https://www.amazon.com/HiLetgo-PCA9685-Channel-12-Bit-Arduino/dp/B07BRS249H/142-4472007-8474650?pd_rd_w=X2d8i&content-id=amzn1.sym.9bef5913-5870-4504-8883-3ba89d7f8e39&pf_rd_p=9bef5913-5870-4504-8883-3ba89d7f8e39&pf_rd_r=8C1Z7T0C2Z2YJHAET4G1&pd_rd_wg=Or3Sj&pd_rd_r=b6a01385-5874-4ce5-a261-6d09b9b0bd0e&pd_rd_i=B07BRS249H&psc=1
