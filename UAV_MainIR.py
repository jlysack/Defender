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
HitDetection_topic = dds.Topic(participant, "HitDetection", DDS.Weapon.HitDetection)

#Writers
HitDetection_writer = dds.DataWriter(participant.implicit_publisher, HitDetection_topic)

#Creating Global Data Holders
HitDetection_data = DDS.Weapon.HitDetection
HitDetection_data.HitBoolean = False
HitDetection_data.HitNumber = 0

#sockid = pylirc.init("IRReceiver.py", blocking=False)
process = subprocess.Popen(["irw"], stdout=subprocess.PIPE)

try:
    while True:
        # Read incoming IR signals
        #output = subprocess.check_output(["irw"]).decode("utf-8")
        output = process.stdout.readline().decode("utf-8")

        if output.strip():
            print("Received signal:", output.strip())

            HitDetection_Data.HitBoolean = True

            HitDetection_writer.write(HitDetection_data)


        
        HitDetection_Data.HitBoolean = False

except KeyboardInterrupt:
    pass


# Clean up the LIRC Connection
#pylirc.deinit()
process.terminate()
