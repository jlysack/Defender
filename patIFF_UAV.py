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
    print("mointor_file called")

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
                # Process the updated contents and extract the value
                # Assuming the value is the first line in the file
                #reported_value = (new_contents.strip().split('\n')[0])
                #print(f"Reported value updated: {reported_value}")

                
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
            #requestUAVIFF_topic.wait_for_data() # wait for a DDS request message
            async for sample in requestUAVIFF_reader.take_data_async():
                
                #responseIFF_data.ObjectIdentity = IFF_CODE
                #print(IFF_CODE)

                if (IFF_CODE == "0"):
                    responseUAVIFF_ReceivedData.ObjectIdentity = 0
                    print("0 successful")
                if (IFF_CODE == "1"):
                    responseUAVIFF_ReceivedData.ObjectIdentity = 1
                    print("1 successful")
                if (IFF_CODE == "2"):
                    responseUAVIFF_ReceivedData.ObjectIdentity = 2
                    print("2 successful")

                #print(IFF_CODE)
                #print("Before message processing")

                #print(f"{sample}")
                # write response back
                
                responseUAVIFF_writer.write(responseUAVIFF_ReceivedData)
                print(responseUAVIFF_ReceivedData.ObjectIdentity)
                print("Reply Message sent")

    await asyncio.sleep(1)

async def UpdateIFF_Code(filename, variable_name):
    global IFF_CODE
    print("Changing Stored IFF Code")
    while True:
        
        async for sample in IFFCode_reader.take_data_async():
            print("Before Code Change processing")

            print(IFFCode_ReceivedData.IFFCode)
            
            IFF_CODE = IFFCode_ReceivedData.IFFCode

##                with open(filename, mode='r') as file:
##                    lines = file.readlines()
##
##                for i, line in enumerate(lines):
##                    if line.startswith(variable_name):
##                        lines[i] = f'{variable_name} = {new_value}\n'
##                        break
##
##                with open(filename, mode='w') as file:
##                    file.writelines(lines)

            #print(f"Successfully updated {variable_name} in {filename}.")
            
            print(f"IFF_Code set to {IFF_CODE}.")
                
##        except FileNotFoundError:
##                print(f'{filename} not found.')
##        except Exception as e:
##                print(f'An error occurred: {str(e)}')

        await asyncio.sleep(1)

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
        asyncio.ensure_future(UpdateIFF_Code(r"C:\Users\Pat Zazzaro\Documents\GitHub\Defender\UAV_IFFCode.txt", "UAV_IFF_CODE")),
        asyncio.ensure_future(ReadIFF_Value()),
        asyncio.ensure_future(WaitforIFF_Response()),
        asyncio.ensure_future(monitor_file())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())
