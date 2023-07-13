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
requestUAVIFF_topic = dds.Topic(participant, "UAVIFFRequest", DDS.IFF.RequestIFF_UAV)
responseUAVIFF_topic = dds.Topic(participant, "UAVIFFResponse", DDS.IFF.ResponseIFF_UAV)
IRSafety_topic = dds.Topic(participant, "IRSafety", DDS.safety.IRSafety)
fireWeapon_topic = dds.Topic(participant, "FireWeapon", DDS.Weapon.FireWeapon)

# Writers
requestUAVIFF_writer = dds.DataWriter(participant.implicit_publisher, requestUAVIFF_topic)

#Readers
IRSafety_reader = dds.DataReader(participant.implicit_subscriber, IRSafety_topic)
fireWeapon_reader = dds.DataReader(participant.implicit_subscriber, fireWeapon_topic)
responseUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, responseUAVIFF_topic)

#Creating global data holders
componentHealth_ReceivedData = DDS.Metrics.ComponentHealth
requestIFF_ReceivedData = DDS.IFF.IFFRequest
responseUAVIFF_ReceivedData = DDS.IFF.ResponseIFF_UAV

IRSafety_data = DDS.safety.IRSafety
IRSafety_data.enabled = 1

fireWeapon_data = DDS.Weapon.FireWeapon
fireWeapon_data.fire = 1
fireWeapon_data.mode = 1

# initalize variables at beginning of script
currentIFFState = "Unknown"
IR_Safety = True
IFF_CODE=0

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

            print("IFF Code Set!")
            print(IFF_CODE)
            
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
    while True:
        async for data in fireWeapon_reader.take_data_async():
            global IFF_CODE
            global IR_Safety
    
            print("Preparing to Fire Weapon...")

            print(IFF_CODE)
            print(IR_Safety)

            if (IFF_CODE == 2) and (IR_Safety == False):
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False) 

                GPIO.setup(22,GPIO.OUT) #EN 
                GPIO.setup(27,GPIO.OUT) #A0 
                GPIO.setup(17,GPIO.OUT) #A1

                GPIO.output(22,GPIO.HIGH) #turn on enable

##                #Establish start of sweep#
##                X = "GPIO.HIGH"
##                Y = "GPIO.HIGH"
##
##                for i in range(4):                
##                    #GPIO.output(27,GPIO.HIGH) 
##                    #GPIO.output(17,GPIO.HIGH)
##
##                    GPIO.output(27,X) 
##                    GPIO.output(17,Y)
##                
##                    subprocess.call(["irsend","SEND_ONCE","Technics_EUR646497","KEY_POWER"])
##
##                    X = "GPIO.LOW" if i == 0 or i == 2 else "GPIO.HIGH"
##                    Y = "GPIO.LOW" if i == 1 or i == 2 else "GPIO.HIGH"
##
##                    if i == 2:
##                        X = "GPIO.HIGH"
##                        Y = "GPIO.HIGH"

                GPIO.output(27,GPIO.HIGH) 
                GPIO.output(17,GPIO.HIGH)
                subprocess.call(["irsend","SEND_ONCE","Technics_EUR646497","KEY_POWER"])

                time.sleep(0.5)

                GPIO.output(27,GPIO.LOW) 
                GPIO.output(17,GPIO.HIGH)
                subprocess.call(["irsend","SEND_ONCE","Technics_EUR646497","KEY_POWER"])

                time.sleep(0.5)

                GPIO.output(27,GPIO.HIGH) 
                GPIO.output(17,GPIO.LOW)
                subprocess.call(["irsend","SEND_ONCE","Technics_EUR646497","KEY_POWER"])

                time.sleep(0.5)

                GPIO.output(27,GPIO.LOW) 
                GPIO.output(17,GPIO.LOW)
                subprocess.call(["irsend","SEND_ONCE","Technics_EUR646497","KEY_POWER"])

                time.sleep(0.5)
                

                # Turn off GPIOs 
                GPIO.output(22,GPIO.LOW) 
                GPIO.output(27,GPIO.LOW) 
                GPIO.output(17,GPIO.LOW)

                print('Complete')
                
            if (IFF_CODE == 1) and (IR_Safety == False):
                print("Target Friend... Standing down")

            if (IFF_CODE == 0) and (IR_Safety == False):
                print("Target Unknown... initiating IFF Request")

                #async for sample in requestIFF_reader.take_data_async():
                requestUAVIFF_writer.write(requestIFF_ReceivedData)
                print("Request")

                await update_IFFCode()
                print("IFF Code Set!")
                print(IFF_CODE)

                    
            if (IFF_CODE == 0) and (IR_Safety == True):
                print("Target Unknown... initiating IFF Request")

                #async for sample in requestIFF_reader.take_data_async():
                requestUAVIFF_writer.write(requestIFF_ReceivedData)
                print("Request")

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
