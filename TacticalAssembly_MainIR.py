import time
import sys
import rti.connextdds as dds
import rti.asyncio
import asyncio
import aiofiles
from interfaces import DDS
import subprocess

#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
componentHealth_topic = dds.Topic(participant, "ComponentHealth", DDS.Metrics.ComponentHealth)
responseUAVIFF_topic = dds.Topic(participant, "UAVIFFResponse", DDS.IFF.ResponseIFF_UAV)
IRSafety_topic = dds.Topic(participant, "IRSafety", DDS.safety.IRSafety)
fireWeapon_topic = dds.Topic(participant, "FireWeapon", DDS.Weapon.FireWeapon)

#Readers
IRSafety_reader = dds.DataReader(participant.implicit_subscriber, IRSafety_topic)
fireWeapon_reader = dds.DataReader(participant.implicit_subscriber, fireWeapon_topic)
responseUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, responseUAVIFF_topic)

#Creating global data holders
componentHealth_ReceivedData = DDS.Metrics.ComponentHealth
responseUAVIFF_ReceivedData = DDS.IFF.ResponseIFF_UAV

IRSafety_data = DDS.safety.IRSafety
IRSafety_data.enabled = 1

fireWeapon_data = DDS.Weapon.FireWeapon
fireWeapon_data.fire = 1
fireWeapon_data.mode = 1

# initalize variables at beginning of script
currentIFFState = "Unknown"
IRSafety = True

async def update_IFFCode():
    global currentIFFState
    global IFF_CODE
    
    while True:
        async for data in responseUAVIFF_reader.take_data_async():
            global responseUAVIFF_ReceivedData
            responseUAVIFF_ReceivedData = data

            print("recieved an IFF response")
            print(responseUAVIFF_ReceivedData.ObjectIdentity)

            if (responseUAVIFF_ReceivedData.ObjectIdentity == 0):
                currentIFFState = "Unknown"
                IFF_CODE = 0
            if (responseUAVIFF_ReceivedData.ObjectIdentity == 2):
                currentIFFState = "Foe"
                IFF_CODE = 2
            if (responseUAVIFF_ReceivedData.ObjectIdentity == 1):
                currentIFFState = "Friend"
                IFF_CODE = 1
            
        await asyncio.sleep(1)

# Update recieved IR safety message
async def update_IRSafeLock():
    global IR_Safety
    while True:
        async for data in IRSafety_reader.take_data_async():
            IRSafety_data = data

            IR_Safety_condition = IRSafety_data.enabled
            print(IR_Safety_condition)

            if (IR_Safety_condition == 0):
                IR_Safety = True
            if (IR_Safety_condition == 1):
                IR_Safety = False

            print(IR_Safety)

    await asyncio.sleep(1)

# Calling a IR blast
async def fire_IRWeapon():
    global IFF_CODE
    global IR_Safety
    
    while True:
        async for data in fireWeapon_reader.take_data_async():
            print("Preparing to Fire Weapon...")

            if (IFF_CODE == 2) and (IR_Safety == False):
                subprocess.call(["irsend","SEND_START","ac","KEY_POWER"])
            if (IFF_CODE == 1) and (IR_Safety == False):
                print("Target Friend... Standing down")
            if (IFF_CODE == 1) and (IR_Safety == True):
                print("Target Friend... Standing down")

    await asyncio.sleep(1)


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
