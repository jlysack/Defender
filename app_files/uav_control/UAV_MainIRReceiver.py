import time
import sys
import rti.connextdds as dds
import rti.asyncio
import asyncio
import aiofiles
from interfaces import DDS
import subprocess
import RPi.GPIO as GPIO 
import time 
import os 

#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
componentHealth_topic = dds.Topic(participant, "ComponentHealth", DDS.Metrics.ComponentHealth)
fireWeapon_topic = dds.Topic(participant, "FireWeapon", DDS.Weapon.FireWeapon)

#Readers
IRSafety_reader = dds.DataReader(participant.implicit_subscriber, IRSafety_topic)
fireWeapon_reader = dds.DataReader(participant.implicit_subscriber, fireWeapon_topic)

#Creating global data holders
componentHealth_ReceivedData = DDS.Metrics.ComponentHealth

fireWeapon_data = DDS.Weapon.FireWeapon
fireWeapon_data.fire = 1
fireWeapon_data.mode = 1





# Define the main loop routine
async def main_loop():
    while True:
        print("Main loop")
        await asyncio.sleep(1)  # Simulating some work and slow thread so we can read it

async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(update_IFFCode()),
        asyncio.ensure_future(update_IRSafeLock()),
        asyncio.ensure_future(fire_IRWeapon())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())
