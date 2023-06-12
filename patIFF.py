import time
#import RPi.GPIO as GPIO
import sys
#sys.path.insert(0, '/home/jlysack')
#from RpiMotorLib import A4988Nema
import rti.connextdds as dds
import rti.asyncio
import asyncio #Need both
from interfaces import DDS

#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
componentHealth_topic = dds.Topic(participant, "ComponentHealth", DDS.Metrics.ComponentHealth)
requestIFF_topic = dds.Topic(participant, "IFFRequest", DDS.IFF.IFFRequest)
responseIFF_topic = dds.Topic(participant, "IFFResponse", DDS.IFF.IFFResponse)

#Define Writers
requestIFF_writer = dds.DataWriter(participant.implicit_publisher, requestIFF_topic)

#Readers
componentHealth_reader = dds.DataReader(participant.implicit_subscriber, componentHealth_topic)
requestIFF_reader = dds.DataReader(participant.implicit_subscriber, requestIFF_topic)
responseIFF_reader = dds.DataReader(participant.implicit_subscriber, responseIFF_topic)


#Creating global data holders, these act as data pointers essentially, I wrote this code coming from a C++ background so excuse any weird-ness
componentHealth_ReceivedData = DDS.Metrics.ComponentHealth
requestIFF_ReceivedData = DDS.IFF.IFFRequest
responseIFF_ReceivedData = DDS.IFF.IFFResponse



# ----------------------

#Define message/data containers for sending
scanResponse_SendingData = DDS.Scanning.ScanResponse
scanResponse_SendingData.ZoneNumber = 2

# -------------------------------------------------

currentIFFState = "Unknown"

# Main Body of Code #

#async def request_IFF():



async def formatresponse_IFF():
    while True:
        print("Recieved IFF Response, formatting....")
        try:
            global currentIFFState
            print(currentIFFState)

            if (currentIFFState == "Foe"):
                print("UAV is Foe")
            if (currentIFFState == "Friend"):
                print("UAV is Friend")
            if (currentIFFState == "Unknown"):
                print("UAV is Unknown")

        except Exception as e:
            print(f"Error in formatresponse_IFF(): {e}")

# Define the main loop routine
async def main_loop():
    #Tell the main thread to use the global variables

    while True:
        print("Main loop")
        await asyncio.sleep(2)  # Simulating some work and slow thread so we can read it
        print("Test, after Main loop sleep")


async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(formatresponse_IFF()),
        #asyncio.ensure_future(update_scanInstruction()),
        #asyncio.ensure_future(update_motorLogic())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())


