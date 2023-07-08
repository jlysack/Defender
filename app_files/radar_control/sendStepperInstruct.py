#!/usr/bin/python3

import time
import sys
import rti.connextdds as dds
from interfaces import DDS


class ddsWriter:

    #Participant
    participant = dds.DomainParticipant(domain_id=1)

    #Topics
    scanInstruction_topic = dds.Topic(participant, "ScanInstruction", DDS.Scanning.ScanInstruction)

    #Writers
    scanInstruction_writer = dds.DataWriter(participant.implicit_publisher, scanInstruction_topic)  

    #Creating data objects and filling
    #userinput = input("zone?: ")

    #ScanInstruction - Can write it as a 1 liner or assign things after, or mix.
    #scanInstruction_data = DDS.Scanning.ScanInstruction(radarSetting = 1, manualScanSetting = 2)
    scanInstruction_data = DDS.Scanning.ScanInstruction
    scanInstruction_data.radarSetting = 1

    #Loop data sending
    while True:
        # Catch control-C interrupt
        try:
            userinput = input("Zone?: ")
            user_input = int(userinput)
            scanInstruction_data.manualScanSetting = user_input #Change this to 1 2 or 3 and restart the code!

            userinput = input("Rad Enabled? (True/False): ")
            if userinput == "True":
                user_input = True
            elif userinput == "False":
                user_input = False
            else:
                user_input = True
            scanInstruction_data.RadEnable = user_input

            #ScanInstruction
            scanInstruction_writer.write(scanInstruction_data)

        #Catch control-C interrupt
        except KeyboardInterrupt:
            break
