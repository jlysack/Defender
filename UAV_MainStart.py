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

message_script_mapping = {
    "message5": [r"/home/Multiverse/Defender/UAV_MainIFF.py"],
    "message6": [r"/home/Multiverse/Defender/UAV_MainIRReceiver.py"],
    "All": [r"/home/Multiverse/Defender/UAV_MainIFF.py", r"/home/Multiverse/Defender/UAV_MainIRReceiver.py"],
    "stop_processes": None  # Special message to stop subprocesses
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

# Main function to start the script
def main():
    # Start the DDS message receiver asynchronously
    loop = asyncio.get_event_loop()
    loop.run_until_complete(receive_dds_messages())

# Entry point of the script
if __name__ == "__main__":
    main()
