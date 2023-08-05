#import pylirc
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

#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
componentHealth_topic = dds.Topic(participant, "ComponentHealth", DDS.Metrics.ComponentHealth)
HitDetection_topic = dds.Topic(participant, "HitDetection", DDS.Weapon.HitDetection)
requestUAVIFF_topic = dds.Topic(participant, "UAVIFFRequest", DDS.IFF.RequestIFF_UAV)
responseUAVIFF_topic = dds.Topic(participant, "UAVIFFResponse", DDS.IFF.ResponseIFF_UAV)
IRSafety_topic = dds.Topic(participant, "IRSafety", DDS.safety.IRSafety)
fireWeapon_topic = dds.Topic(participant, "FireWeapon", DDS.Weapon.FireWeapon)

#Writers
componentHealth_writer = dds.DataWriter(participant.implicit_publisher, componentHealth_topic)
HitDetection_writer = dds.DataWriter(participant.implicit_publisher, HitDetection_topic)
requestUAVIFF_writer = dds.DataWriter(participant.implicit_publisher, requestUAVIFF_topic)

#Readers
IRSafety_reader = dds.DataReader(participant.implicit_subscriber, IRSafety_topic)
fireWeapon_reader = dds.DataReader(participant.implicit_subscriber, fireWeapon_topic)
responseUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, responseUAVIFF_topic)

#Creating Global Data Holders
HitDetection_data = DDS.Weapon.HitDetection
HitDetection_data.HitBoolean = False
HitDetection_data.HitNumber = 0

IRSafety_data = DDS.safety.IRSafety
IRSafety_data.enabled = 1

fireWeapon_data = DDS.Weapon.FireWeapon
fireWeapon_data.fire = 1
fireWeapon_data.mode = 1

componentHealth_data = DDS.Metrics.ComponentHealth()
componentHealth_data.Name = "UAV_IR"
componentHealth_data.State = 1

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

def fire_onboard_IRLED():
    
    IR_LED_PIN = 22
    #ir_led = LED(IR_LED_PIN)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IR_LED_PIN, GPIO.OUT)

    GPIO.output(IR_LED_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(IR_LED_PIN, GPIO.LOW)

def capture_raw_ir():
    process = subprocess.Popen(['sudo', 'mode2', '-d', '/dev/lirc0'], stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if not line:
            break
        yield line.decode('utf-8')

# Calling a IR blast
async def fire_IRWeapon():
    while True:
        async for data in fireWeapon_reader.take_data_async():
            global IFF_CODE
            global IR_Safety
            global fireWeapon_data  
            fireWeapon_data = data;
            print("Preparing to Fire Weapon...")

            if (IFF_CODE == 2) and (IR_Safety == False) and (fireWeapon_data.fire==True) and (fireWeapon_data.mode==1):
                

                print('Complete')
                
            if (IFF_CODE == 1) and (IR_Safety == False):
                print("Target Friend... Standing down")

            if (IFF_CODE == 0) and (IR_Safety == False):
                print("Target Unknown... initiating IFF Request")
                
                #async for sample in requestIFF_reader.take_data_async():
                requestUAVIFF_writer.write(requestIFF_ReceivedData)

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

                if (IFF_CODE == 2):
                    

                    print('Complete')
                if (IFF_CODE == 1):
                    print("ID'd friend standing down")

                    
            if (IFF_CODE == 0) and (IR_Safety == True):
                print("Target Unknown... initiating IFF Request")
                #async for sample in requestIFF_reader.take_data_async():
                requestUAVIFF_writer.write(requestIFF_ReceivedData)

    await asyncio.sleep(1)


async def main_execution_loop():
    try:
        for signal in capture_raw_ir():
            print("Captured signal:", signal.strip())

            HitDetection_data.HitBoolean = True
            HitDetection_writer.write(HitDetection_data)

            print(HitDetection_data)

        HitDetection_data.HitBoolean = False
        HitDetection_writer.write(HitDetection_data)

# Define the main loop routine
async def main_loop():
    while True:
        print("Main loop")
        # Debugging portion of script
        # Checks if DDS Entities are Active
        if not participant.enabled:
            print("Participant is not enabled.")
            return

        if not componentHealth_writer.enabled:
            print("ComponentHealth DataWriter is not enabled.")
            return

        if not HitDetection_writer.enabled:
            print("ComponentHealth DataWriter is not enabled.")
            return

        # Write Component status
        try:
            componentHealth_writer.write(componentHealth_data)
            print(componentHealth_data)
        except Exception as e:
            print(f"Error in writing componentHealth_data: {e}")
        await asyncio.sleep(1)
        

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


##if __name__ == "__main__":
##    for signal in capture_raw_ir():
##        print("Captured signal:", signal.strip())
##
##        HitDetection_data.HitBoolean = True
##        HitDetection_writer.write(HitDetection_data)
##
##        print(HitDetection_data)
##
##    HitDetection_data.HitBoolean = False
##    HitDetection_writer.write(HitDetection_data)
    
