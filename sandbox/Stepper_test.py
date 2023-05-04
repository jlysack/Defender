#!/usr/bin/env python3

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


    # ====================== section A ===================
    print("TEST SECTION A")
    print("Pivot CClockwise 22.5degrees")
    input("Press <Enter> to pivot CClockwise 22.5degrees")
    mymotortest.motor_go(False, "1/8", 100, .005, True, .05)
    time.sleep(1)
    motor_go(clockwise, steptype", steps, stepdelay, verbose, initdelay)
    input("TEST: Press <Enter> to continue  Full 180 turn Test1")
    mymotortest.motor_go(False, "Full", 100, .05, False, .05)
    time.sleep(1)
    input("TEST: Press <Enter> to continue  full 180 clockwise Test2")
    mymotortest.motor_go(True, "Full", 100, .05, True, .05)
    time.sleep(1)
    input("TEST: Press <Enter> to continue  full 180 no verbose Test3")
    mymotortest.motor_go(False, "Full", 100, .05, False, .05)
    time.sleep(1)
    input("TEST: Press <Enter> to continue  timedelay Test4")
    mymotortest.motor_go(True, "Full", 10, 1, True, .05)
    time.sleep(1)
    input("TEST: Press <Enter> to continue  full initdelay Test5")
    mymotortest.motor_go(True, "Full", 90, .01, True, 10)
    time.sleep(1)

    # ========================== section B =========================
    print("TEST SECTION B")

    motor_go(clockwise, steptype", steps, stepdelay, verbose, initdelay)
    input("TEST: Press <Enter> to continue  half Test6")
    mymotortest.motor_go(False, "Half", 400, .005, True, .05)
    time.sleep(1)

    input("TEST: Press <Enter> to continue 1/ 4 Test7")
    mymotortest.motor_go(False, "1/4", 800, .005, True, .05)
    time.sleep(1)
    input("TEST: Press <Enter> to continue 1/8 Test8")
    mymotortest.motor_go(False, "1/8", 1600, .005, True, .05)
    time.sleep(1)

    input("TEST: Press <Enter> to continue  1/16 Test9")
    mymotortest.motor_go(False, "1/16", 3200, .005, True, .05)
    time.sleep(1)

# ===================MAIN===============================

if __name__ == '__main__':
    print("TEST START")
    main()
    GPIO.cleanup()
    print("TEST END")
    exit()

# =====================END===============================
