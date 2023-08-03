#import pylirc
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
HitDetection_topic = dds.Topic(participant, "HitDetection", DDS.Weapon.HitDetection)

#Writers
componentHealth_writer = dds.DataWriter(participant.implicit_publisher, componentHealth_topic)
HitDetection_writer = dds.DataWriter(participant.implicit_publisher, HitDetection_topic)

#Creating Global Data Holders
HitDetection_data = DDS.Weapon.HitDetection
HitDetection_data.HitBoolean = False
HitDetection_data.HitNumber = 0

componentHealth_data = DDS.Metrics.ComponentHealth()
componentHealth_data.Name = "UAV_IR"
componentHealth_data.State = 1

##process = subprocess.Popen(["irw"], stdout=subprocess.PIPE)

##async def main_execution_loop():
##    try:
##        while True:
##            output = process.stdout.readline().decode("utf-8")
##
##            if output.strip():
##                print("Received signal:", output.strip())
##
##                HitDetection_data.HitBoolean = True
##
##                HitDetection_writer.write(HitDetection_data)
##
##            HitDetection_data.HitBoolean = False
##
##    except KeyboardInterrupt:
##        componentHealth_data.State = 0
##        componentHealth_writer.write(componentHealth_data)
##
##        # Clean up the LIRC Connection
##        process.terminate()
##        
##        #pass

async def read_irw_output():
    process = await asyncio.create_subprocess_exec(
        "irw",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        while True:
            #output = await process.stdout.readlines()
            output = await asyncio.wait_for(process.stdout.read(100), timeout=1.0)
            if not output:
                break

            line = output.decode("utf-8").strip()
            if line:
                print("Recieved IR signal:", line)

                HitDetection_data.HitBoolean = True
                HitDetection_writer.write(HitDetection_data)

            HitDetection_data.HitBoolean = False

    except asyncio.CancelledError:
        process.terminate()
        await process.wait()
    except Exception as e:
        print(f"Error while reading irw output: {e}")
    finally:
        process.terminate()
        await process.wait()

async def main_execution_loop():
    try:
        await read_irw_output()
    except asyncio.CancelledError:
        pass
    finally:
        componentHealth_data.State = 0
        componentHealth_writer.write(componentHealth_data)

async def main_loop():
    global componentHealth_data
    
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
        asyncio.ensure_future(main_execution_loop())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())
