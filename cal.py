import time
import RPi.GPIO as GPIO
import sys
from RpiMotorLib import A4988Nema

# Microstep Resolution MS1-MS3 -> GPIO Pin , can be set to (-1,-1,-1) to turn off
GPIO_pins = (25, 8, 7)
direction = 12  # Direction -> GPIO Pin
step = 1  # Step -> GPIO Pin
mymotortest = A4988Nema(direction, step, GPIO_pins, "A4988")

def move_left():
    print("Moving left one step")
    mymotortest.motor_go(False,"1/8", 50,.005,False,.05)

def move_right():
    print("Moving right one step")
    mymotortest.motor_go(True,"1/8", 50,.005,False,.05)


def move_far_left():
    print("Moving left three steps")
    mymotortest.motor_go(False,"1/8", 3,.005,False,.05)

def move_far_right():
    print("Moving right three steps")
    mymotortest.motor_go(True,"1/8", 3,.005,False,.05)

def main():
    while True:
        user_input = input("Enter a command (a: move left, A: move far left, d: move right, D: move far right, q: quit): ")
        
        if user_input == "a":
            move_left()
        elif user_input == "d":
            move_right()
        elif user_input == "A":
            move_far_left()
        elif user_input == "D":
            move_far_right()
        elif user_input == "q":
            print("Quitting the program...")
            break
        else:
            print("Invalid command. Try again.")

if __name__ == "__main__":
    main()
