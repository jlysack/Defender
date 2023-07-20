import time
#import RPi.GPIO as GPIO
import sys
#from RpiMotorLib import A4988Nema
import rti.connextdds as dds
import rti.asyncio
import asyncio #Need both
from interfaces import DDS
import subprocess
import os
import signal

# Microstep Resolution MS1-MS3 -> GPIO Pin , can be set to (-1,-1,-1) to turn off
GPIO_pins = (25, 8, 7)
direction = 12  # Direction -> GPIO Pin
step = 1  # Step -> GPIO Pin
#mymotortest = A4988Nema(direction, step, GPIO_pins, "A4988")

#Participant
participant = dds.DomainParticipant(domain_id=1)

# Topics
Command_topic = dds.Topic(participant, "Command", DDS.misc.Command)

# Reader
Command_Reader = dds.DataReader(participant.implicit_subscriber, Command_topic)

# Message Data
Command_data = DDS.misc.Command

### DDS Mapping
##message_script_mapping = {
##    "a": move_left(),
##    "A": move_far_left(),
##    "d": move_right(),
##    "D": move_far_right(),
##    "stop_processes": None  # Special message to stop subprocesses
##}

def process_message(data):

    command = data
    #print(command)

    if command == 'a':
        move_left()
    elif command == 'A':
        move_far_left()
    elif command == 'd':
        move_right()
    elif command == 'D':
        move_far_right()
    else:
        print("unknown command...")
        

def move_left():
    print("Moving left one step")
    #mymotortest.motor_go(False,"1/8", 50,.005,False,.05)

def move_right():
    print("Moving right one step")
    #mymotortest.motor_go(True,"1/8", 50,.005,False,.05)

def move_far_left():
    print("Moving left three steps")
    #mymotortest.motor_go(False,"1/8", 150,.005,False,.05)

def move_far_right():
    print("Moving right three steps")
    #mymotortest.motor_go(True,"1/8", 150,.005,False,.05)

##def main():
##    while True:
##        user_input = input("Enter a command (a: move left, A: move far left, d: move right, D: move far right, q: quit): ")
##        
##        if user_input == "a":
##            move_left()
##        elif user_input == "d":
##            move_right()
##        elif user_input == "A":
##            move_far_left()
##        elif user_input == "D":
##            move_far_right()
##        elif user_input == "q":
##            print("Quitting the program...")
##            break
##        else:
##            print("Invalid command. Try again.")

# Asynchronous DDS message receiver
async def receive_dds_messages():
    while True:
        # Check if the received message has a corresponding script
        async for message in Command_Reader.take_data_async():
            message_data = message

            print(message_data)

            if message_data.Destination == 'Calibration':
                process_message(message_data.Command)


    await asyncio.sleep(1)

async def main_loop():
    while True:
        print("main loop")
        await asyncio.sleep(1)

async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(receive_dds_messages())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())
