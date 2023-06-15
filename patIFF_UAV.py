import time
import sys
import rti.connextdds as dds
import rti.asyncio
import asyncio
import aiofiles
from interfaces import DDS

#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
componentUAVIFFHealth_topic = dds.Topic(participant, "UAVIFFComponentHealth", DDS.Metrics.ComponentHealth)
requestIFF_topic = dds.Topic(participant, "IFFRequest", DDS.IFF.IFFRequest)
responseIFF_topic = dds.Topic(participant, "IFFResponse", DDS.IFF.IFFResponse)
requestUAVIFF_topic = dds.Topic(participant, "UAVIFFRequest", DDS.IFF.IFFRequest.UAV)
responseUAVIFF_topic = dds.Topic(participant, "UAVIFFResponse", DDS.IFF.IFFResponse.UAV)

#Define Writers
responseUAVIFF_writer = dds.DataWriter(participant.implicit_publisher, responseUAVIFF_topic)

#Readers
componentUAVIFFHealth_reader = dds.DataReader(participant.implicit_subscriber, componentUAVIFFHealth_topic)
requestUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, requestUAVIFF_topic)
requestIFF_reader = dds.DataReader(participant.implicit_subscriber, requestIFF_topic)

#Recieved Data
componentUAVIFFHealth_ReceivedData = DDS.Metrics.ComponentHealth
requestUAVIFF_ReceivedData = DDS.IFF.IFFRequest.UAV
responseUAVIFF_ReceivedData = DDS.IFF.IFFResponse.UAV
requestIFF_data = DDS.IFF.IFFRequest


async def find_variable_value(contents, search_string):
    lines = contents.split('\n')
    for line in lines:
        if search_string in line:
            variable_value = line.split(search_string)[1].strip()
            return variable_value
    return None

async def ReadIFF_Value():
    global IFF_CODE
    
    async with aiofiles.open("UAV_IFFCode.txt", mode='r') as file:
        contents = await file.read()

        IFF_CODE = await find_variable_value(contents, "UAV_IFF_CODE=")
        return IFF_CODE

async def WaitforIFF_Response():
    global IFF_CODE

    await asyncio.sleep(1)
    
    while True:
            #requestUAVIFF_topic.wait_for_data() # wait for a DDS request message
            #await asyncio.sleep(0.1)
            
            #received_IFFRequest = requestUAVIFF_reader.take_data_async()

            print("Before message processing")
            async for sample in requestIFF_reader.take_data_async():
                
                #responseIFF_data.ObjectIdentity = IFF_CODE


                print(f"{sample}")
                # write response back
                responseUAVIFF_writer.write(responseUAVIFF_ReceivedData)
                print("Reply Message sent")

# Define the main loop routine
async def main_loop():
    #Tell the main thread to use the global variables
    global IFF_CODE

    while True:
        print("Main loop")
        await asyncio.sleep(2)  # Simulating some work and slow thread so we can read it

        # Test Print Outs
        #print(f"The variable of the IFF code is: {IFF_CODE}")

async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(ReadIFF_Value()),
        asyncio.ensure_future(WaitforIFF_Response()),
        #asyncio.ensure_future(update_motorLogic())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())
