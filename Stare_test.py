import time
import RPi.GPIO as GPIO

import sys
sys.path.insert(0, '/home/jlysack')
from RpiMotorLib import A4988Nema

# Production installed library import
# from RpiMotorLib import RpiMotorLib

def main():
	# ====== Tests for motor ======

	# Microstep Resolution MS1-MS3 -> GPIO Pin , can be set to (-1,-1,-1) to turn off
    GPIO_pins = (25, 8, 7)
    direction = 12  # Direction -> GPIO Pin
    step = 1  # Step -> GPIO Pin

    # Declare an named instance of class pass GPIO-PINs
    # (self, direction_pin, step_pin, mode_pins , motor_type):
    mymotortest = A4988Nema(direction, step, GPIO_pins, "A4988")

    # (1) clockwise, type = bool, default = False, help = "Turn stepper counterclockwise"
    # (2) steptype, type = string, default = Full,  (Full, Half, 1 / 4, 1 / 8, 1 / 16)
    # (3) steps, type = int, default = 200, 200 is 360deg rev in Full mode.
    # (4) stepdelay, type = float, default = 0.05
    # (5) verbose, type = bool, default = False, help = "Write pin actions",
    # (6) initdelay, type = float, default = 1mS, help = Intial delay after GPIO pins initialized but before motor is moved.

# ====================== section A ===================

# assuming calibration step is complete, which means that stepper is pointing at EZ 3 to start

    past_ez = "EZ3"
    print("Stepper motor currently pointing at EZ 3")
    print("Which Zone would you like to point to? (1 or 2)\n")
    future_ez = input()
    print(future_ez)

    if future_ez=="1":
        print("Pivoting to EZ1")
        mymotortest.motor_go(False, "1/8", 100, .005, True, .05)
        time.sleep(1)
        past_ez = "1"
        print("Stepper is pointing at EZ1")
    elif future_ez == "2":
        print("Pivoting to EZ2")
        mymotortest.motor_go(True, "1/8", 100, .005, True, .05)
        time.sleep(1)
        past_ez = "2"
        print("Stepper is pointing at EZ2")
    else:
        print("Invalid entry")

    cont="y"

    while(cont=="y"):
        print("Which zone would you like to point to?")
        future_ez = input()
        
        if future_ez=="1":
            if past_ez=="2":
                print("Pivoting to EZ1")
                mymotortest.motor_go(False,"1/8",200,.005,True,.05)
                time.sleep(1)
                past_ez = "1"
                print("Stepper motor is pointing at EZ")
            else:
                print("Pivoting to EZ1\n")
                mymotortest.motor_go(False,"1/8",100,.005,True,.05)
                time.sleep(1)
                past_ez = "1"
                print("Stepper motor is pointing at EZ1")
        elif future_ez=="2":
            if past_ez=="1":
                print("Pivoting to EZ2")
                mymotortest.motor_go(True,"1/8",200,.005,True,.05)
                time.sleep(1)
                past_ez = "2"
                print("Stepper motor is pointing at EZ2")
            else:
                print("Pivoting to EZ3")
                mymotortest.motor_go(True,"1/8",100,.005,True,.05)
                time.sleep(1)
                past_ez = "EZ2"
                print("Stepper motor is pointing at EZ2")
        elif future_ez=="3":
            if past_ez=="1":
                print("Pivoting to EZ3")
                mymotortest.motor_go(True,"1/8",100,.005,True,.05)
                time.sleep(1)
                past_ez = "EZ3"
                print("Stepper motor is pointing at EZ3")
            else:
                print("Pivoting to EZ2")
                mymotortest.motor_go(False,"1/8",100,.005,True,.05)
                time.sleep(1)
                past_ez = "EZ3"
                print("Stepper motor is pointing at EZ3")
        else:
            print("Invalid Input\n")

        print("Would you like to continue? (y or n)")
        cont=input()

# ===================MAIN===============================

if __name__ == '__main__':
    print("TEST START")
    main()
    GPIO.cleanup()
    print("TEST END")
    exit()

    # =====================END===============================
