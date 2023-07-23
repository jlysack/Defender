#!/usr/bin/env python3

import time
import sys
import rti.connextdds as dds
import rti.asyncio
import asyncio #Need both
from interfaces import DDS
import subprocess
import os
import signal

#Participant
participant = dds.DomainParticipant(domain_id=1)

# Topics
Command_topic = dds.Topic(participant, "Command", DDS.misc.Command)

# Reader
Command_Reader = dds.DataReader(participant.implicit_subscriber, Command_topic)

# Old Test Structure
##message_script_mapping = {
##    "message1": [r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\patIFF.py"],
##    "message2": [r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\patIFF_UAV.py"],
##    "message3": ["script3.py"],
##    "All": [r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\patIFF.py", r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\patIFF_UAV.py"],
##    "stop_processes": None  # Special message to stop subprocesses
##}

message_script_mapping = {
    "message1": [r"/home/jlysack/code/Defender/TacticalAssembly_MainIFF.py"],
    "message2": [r"/home/jlysack/code/Defender/TacticalAssembly_MainIR.py"],
    "message3": [r"/home/jlysack/code/Defender/jordanStepper.py"],
    "message4": [r"/home/jlysack/code/Defender/cal_TestDDS.py"],
    "message7": [r"/home/reidm/Defender/app_files/radar_control/defender_main.py"],
    "All": [r"/home/jlysack/code/Defender/TacticalAssembly_MainIFF.py", r"/home/jlysack/code/Defender/TacticalAssembly_MainIR.py", r"/home/jlysack/code/Defender/jordanStepper.py", r"/home/jlysack/code/Defender/cal_TestDDS.py", r"/home/reidm/Defender/app_files/radar_control/defender_main.py"],
    "stop_processes": None
}

# List to store active subprocesses
active_subprocesses = []

# Asynchronous DDS message receiver
async def receive_dds_messages():
    global active_subprocesses
    
    while True:
        try:
            # Check if the received message has a corresponding script
            async for message in Command_Reader.take_data_async():
                script_paths = message_script_mapping.get(message.Command)
                if script_paths is None:

                    print("Hi Jordan")
                    
                    # Handle the exit message
                    stop_all_subprocesses()
                    break
                else:
                    for script_path in script_paths:
                        command = execute_python_script(script_path)


                    print(active_subprocesses)

        except KeyboardInterrupt:
                break

# Execute a Python script
def execute_python_script(script_path):
    process = subprocess.Popen(["python", script_path])
    active_subprocesses.append(process)

# Stop all active subprocesses
def stop_all_subprocesses():
    for process in active_subprocesses:
        print("killing processes...")
        os.kill(process.pid, signal.SIGTERM)

### Main function to start the script
##def main():
##    # Start the DDS message receiver asynchronously
##    loop = asyncio.get_event_loop()
##    loop.run_until_complete(receive_dds_messages())
##
### Entry point of the script
##if __name__ == "__main__":
##    main()

# Define the ma	in loop coroutine
async def main_loop():
    while True:
        print("Main loop")
        await asyncio.sleep(0.5)

async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(receive_dds_messages())
    ]
    await asyncio.gather(*tasks)


asyncio.run(run_event_loop())
