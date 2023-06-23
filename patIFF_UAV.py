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
requestUAVIFF_topic = dds.Topic(participant, "UAVIFFRequest", DDS.IFF.RequestIFF_UAV)
responseUAVIFF_topic = dds.Topic(participant, "UAVIFFResponse", DDS.IFF.ResponseIFF_UAV)
IFFCode_topic = dds.Topic(participant, "IFFCode", DDS.IFF.SetCode)

#Define Writers
responseUAVIFF_writer = dds.DataWriter(participant.implicit_publisher, responseUAVIFF_topic)

#Readers
componentUAVIFFHealth_reader = dds.DataReader(participant.implicit_subscriber, componentUAVIFFHealth_topic)
requestUAVIFF_reader = dds.DataReader(participant.implicit_subscriber, requestUAVIFF_topic)
requestIFF_reader = dds.DataReader(participant.implicit_subscriber, requestIFF_topic)
IFFCode_reader = dds.DataReader(participant.implicit_subscriber, IFFCode_topic)

#Recieved Data
componentUAVIFFHealth_ReceivedData = DDS.Metrics.ComponentHealth
requestUAVIFF_ReceivedData = DDS.IFF.RequestIFF_UAV
responseUAVIFF_ReceivedData = DDS.IFF.ResponseIFF_UAV
requestIFF_data = DDS.IFF.IFFRequest
IFFCode_ReceivedData = DDS.IFF.SetCode


async def find_variable_value(contents, search_string):
    lines = contents.split('\n')
    for line in lines:
        if search_string in line:
            variable_value = line.split(search_string)[1].strip()
            return variable_value
    return None

async def ReadIFF_Value():
    global IFF_CODE
    
    async with aiofiles.open(r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\UAV_IFFCode.txt", mode='r') as file:
        contents = await file.read()
        IFF_CODE = await find_variable_value(contents, "UAV_IFF_CODE=")
        file.close()
        return IFF_CODE

    await asyncio.sleep(1)


async def monitor_file():
    global reported_value

    # Get the initial file size
    file_size = 0

    while True:
        # Open the file in read mode
        with open(r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\UAV_IFFCode.txt", 'r') as file:
            # Move the file pointer to the end
            file.seek(file_size)
            
            # Read the new contents from the file
            new_contents = file.read()

            # Check if there are any updates
            if new_contents:     
                async with aiofiles.open(r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\UAV_IFFCode.txt", mode='r') as file:
                    contents = await file.read()

                    IFF_CODE = await find_variable_value(contents, "UAV_IFF_CODE=")
                    print(IFF_CODE)
                    return IFF_CODE

            # Update the file size
            file_size = file.tell()

            file.close()

        # Sleep for a specified duration before checking the file again
        await asyncio.sleep(1)


async def WaitforIFF_Response():
    global IFF_CODE
    
    while True:    
            async for sample in requestUAVIFF_reader.take_data_async():
                
                print("Right before IFF response....")
                print(IFF_CODE)

                if (IFF_CODE == 0):
                    responseUAVIFF_ReceivedData.ObjectIdentity = 0
                    print("0 successful")
                if (IFF_CODE == 1):
                    responseUAVIFF_ReceivedData.ObjectIdentity = 1
                    print("1 successful")
                if (IFF_CODE == 2):
                    responseUAVIFF_ReceivedData.ObjectIdentity = 2
                    print("2 successful")

                responseUAVIFF_writer.write(responseUAVIFF_ReceivedData)
                print("Reply Message sent")

    await asyncio.sleep(1)

async def UpdateIFF_Code(filename, variable_name):
    global IFF_CODE
  
    while True:
        async for sample in IFFCode_reader.take_data_async():
            print("Before Code Change processing")
            IFFCode_ReceivedData = sample

            if (IFFCode_ReceivedData.IFFCode == 0):
                IFF_CODE = 0
                print("Unknown Set")
            if (IFFCode_ReceivedData.IFFCode == 2):
                IFF_CODE = 2
                print("Enemy Set")
            if (IFFCode_ReceivedData.IFFCode == 1):
                IFF_CODE = 1
                print("Friend Set")
            print(f"IFF_Code set to {IFF_CODE}.")
            
        await asyncio.sleep(1)

# Define the main loop routine
async def main_loop():
    global IFF_CODE

    while True:
        print("Main loop")
        await asyncio.sleep(2)  # Simulating some work and slow thread so we can read it


async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(UpdateIFF_Code(r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\UAV_IFFCode.txt", "UAV_IFF_CODE")),
        asyncio.ensure_future(ReadIFF_Value()),
        asyncio.ensure_future(WaitforIFF_Response()),
        #asyncio.ensure_future(monitor_file())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())
