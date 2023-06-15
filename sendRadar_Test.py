#!/usr/bin/env python3

import time
import sys
import rti.connextdds as dds
from interfaces import DDS


#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
radar_report_topic = dds.Topic(participant, "RadarReport", DDS.SILKTypes.DetectionStruct)

#Writers
radar_report_writer = dds.DataWriter(participant.implicit_publisher, radar_report_topic)

radar_report_data = DDS.SILKTypes.DetectionStruct


radar_report_data.Range        = 10
radar_report_data.Azimuth      = 24.5
radar_report_data.zoneTypeEnum = 1
radar_report_data.ZoneNumber   = 3

radar_report_writer.write(radar_report_data)

#Loop data sending
for count in range(10):
        # Catch control-C interrupt
        try:
            #Print counter
            print(f"Writing data, count {count}")

            #Write the data

            #ScanInstruction
            radar_report_writer.write(radar_report_data)

            time.sleep(0.2)
        except KeyboardInterrupt:
            break
