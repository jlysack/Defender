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

componentHealth_data = DDS.Metrics.ComponentHealth
componentHealth_data.Name = "UAV_IR"
componentHealth_data.State = 1

process = subprocess.Popen(["irw"], stdout=subprocess.PIPE)

try:
    while True:

        print("Main loop")

        try:
            componentHealth_writer.write(componentHealth_data)
            print(componentHealth_data)
        except Exception as e:
            print(f"Error in componentHealth_writer(): {e}")
        
        output = process.stdout.readline().decode("utf-8")

        if output.strip():
            print("Received signal:", output.strip())

            HitDetection_data.HitBoolean = True

            HitDetection_writer.write(HitDetection_data)


        
        HitDetection_data.HitBoolean = False

except KeyboardInterrupt:
    componentHealth_data.State = 0
    componentHealth_writer.write(componentHealth_data)
    pass

# Clean up the LIRC Connection
process.terminate()
