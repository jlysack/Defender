import time
import sys
import rti.connextdds as dds
import rti.asyncio
import asyncio #Need both
from interfaces import DDS

#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
componentUAVIFFHealth_topic = dds.Topic(participant, "UAVIFFComponentHealth", DDS.Metrics.ComponentHealth)
requestUAVIFF_topic = dds.Topic(participant, "UAVIFFRequest", DDS.IFF.IFFRequest.UAV)
responseUAVIFF_topic = dds.Topic(participant, "UAVIFFResponse", DDS.IFF.IFFResponse.UAV)

#Define Writers
requestUAVIFF_writer = dds.DataWriter(participant.implicit_publisher, requestUAVIFF_topic)

#Readers
componentUAVIFFHealth_reader = dds.DataReader(participant.implicit_subscriber, componentUAVIFFHealth_topic)
requestUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, requestUAVIFF_topic)
responseUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, responseUAVIFF_topic)

#Recieved Data
componentUAVIFFHealth_ReceivedData = DDS.Metrics.ComponentHealth
requestUAVIFF_ReceivedData = DDS.IFF.IFFRequest.UAV
responseUAVIFF_ReceivedData = DDS.IFF.IFFResponse.UAV


async def sendIFFResponse():
    global



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
        asyncio.ensure_future(update_IFFCode()),
        asyncio.ensure_future(formatresponse_IFF()),
        #asyncio.ensure_future(update_motorLogic())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())
