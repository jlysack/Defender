import time
import sys
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
requestUAVIFF_topic = dds.Topic(participant, "UAVIFFRequest", DDS.IFF.RequestIFF_UAV)
responseUAVIFF_topic = dds.Topic(participant, "UAVIFFResponse", DDS.IFF.ResponseIFF_UAV)

#Define Writers
responseIFF_writer = dds.DataWriter(participant.implicit_publisher, responseIFF_topic) # Send IFF Back to SADT
requestUAVIFF_writer = dds.DataWriter(participant.implicit_publisher, requestUAVIFF_topic) # Send IFF Request to UAV

componentHealth_reader = dds.DataReader(participant.implicit_subscriber, componentHealth_topic)

#Readers (Between SADT to Tactical Assembly)
requestIFF_reader = dds.DataReader(participant.implicit_subscriber, requestIFF_topic) # Request for IFF from SADT

#Readers (Between Tactical Assembly to UAV)
responseUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, responseUAVIFF_topic)
requestUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, requestUAVIFF_topic)

#Creating global data holders, these act as data pointers essentially, I wrote this code coming from a C++ background so excuse any weird-ness
componentHealth_ReceivedData = DDS.Metrics.ComponentHealth
requestIFF_ReceivedData = DDS.IFF.IFFRequest
responseIFF_ReceivedData = DDS.IFF.IFFResponse
responseUAVIFF_ReceivedData = DDS.IFF.ResponseIFF_UAV

currentIFFState = "Unknown"

# Main Body of Code #
async def update_IFFCode():
    global currentIFFState
    
    while True:
        #print("Updating IFF Code based on recieved input.....")
        async for data in responseUAVIFF_reader.take_data_async():
            global responseUAVIFF_ReceivedData
            responseUAVIFF_ReceivedData = data

            print("recieved an IFF response")

            print(responseUAVIFF_ReceivedData.ObjectIdentity)

            responseIFF_ReceivedData.ObjectIdentity = responseUAVIFF_ReceivedData.ObjectIdentity

            if (responseUAVIFF_ReceivedData.ObjectIdentity == 0):
                currentIFFState = "Unknown"
            if (responseUAVIFF_ReceivedData.ObjectIdentity == 2):
                currentIFFState = "Foe"
            if (responseUAVIFF_ReceivedData.ObjectIdentity == 1):
                currentIFFState = "Friend"
                print("1")

            print(currentIFFState)

            if (currentIFFState == "Foe"):
                print("UAV is Foe")
            if (currentIFFState == "Friend"):
                print("UAV is Friend")
            if (currentIFFState == "Unknown"):
                print("UAV is Unknown")
            
            responseIFF_writer.write(responseIFF_ReceivedData)
            print("Dashboard IFF Response sent!")
            
        await asyncio.sleep(1)

async def WaitforIFF_DashboardRequest():
    while True:
        print("Before processing Dashboard Request")

        async for sample in requestIFF_reader.take_data_async():
            requestUAVIFF_writer.write(requestIFF_ReceivedData)
            print("Request")

    await asyncio.sleep(1)

# Define the main loop routine
async def main_loop():
    while True:
        print("Main loop")
        await asyncio.sleep(2)  # Simulating some work and slow thread so we can read it


async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(WaitforIFF_DashboardRequest()),
        asyncio.ensure_future(update_IFFCode()),
        #asyncio.ensure_future(WritetoDashboard_IFF())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())


