#!/usr/bin/python3

import time
import sys
import rti.connextdds as dds
from interfaces import DDS


class ddsWriter:

    #Participant
    participant = dds.DomainParticipant(domain_id=1)

    #Topics
    radarSafety_topic = dds.Topic(participant, "RadarSafety", DDS.safety.RadarSafety)

    #Writers
    radarSafety_writer = dds.DataWriter(participant.implicit_publisher, radarSafety_topic)  

    #Creating data objects and filling
    #userinput = input("zone?: ")

    #radarSafety - Can write it as a 1 liner or assign things after, or mix.
    #radarSafety_data = DDS.Scanning.radarSafety(radarSetting = 1, manualScanSetting = 2)
    radarSafety_data = DDS.safety.RadarSafety

    radarSafety_data.enabled = True

    #Loop data sending
    while True:
        # Catch control-C interrupt
        try:
            userinput = input("Rad Enabled? (Y/N): ")
            if userinput == "Y":
                user_input = True
            elif userinput == "N":
                user_input = False
            else:
                user_input = True
            radarSafety_data.enabled = user_input

            #radarSafety
            radarSafety_writer.write(radarSafety_data)

        #Catch control-C interrupt
        except KeyboardInterrupt:
            break
