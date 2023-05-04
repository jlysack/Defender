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
    mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "A4988")

    # (1) clockwise, type = bool, default = False, help = "Turn stepper counterclockwise"
    # (2) steptype, type = string, default = Full,  (Full, Half, 1 / 4, 1 / 8, 1 / 16)
    # (3) steps, type = int, default = 200, 200 is 360deg rev in Full mode.
    # (4) stepdelay, type = float, default = 0.05
    # (5) verbose, type = bool, default = False, help = "Write pin actions",
    # (6) initdelay, type = float, default = 1mS, help = Intial delay after GPIO pins initialized but >

# ====================== section A ===================
    print("Pivot CClockwise 22.5degrees")
    input("Press <Enter> to pivot CClockwise 22.5degrees")
    mymotortest.motor_go(False, "1/8", 100, .005, True, .05)
    time.sleep(1)

    # ===================MAIN===============================

    if __name__ == '__main__':
        print("TEST START")
        main()
        GPIO.cleanup()
        print("TEST END")
        exit()

    # =====================END===============================
