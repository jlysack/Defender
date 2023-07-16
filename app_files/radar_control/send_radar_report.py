#!/usr/bin/env python3

import time
import sys
import rti.connextdds as dds
from interfaces import DDS


class ddsWriter:
    def __init__(self):
        # Participant
        self.participant = dds.DomainParticipant(domain_id=1)

        # Topics
        self.radar_report_topic = dds.Topic(
            self.participant, "RadarReport", DDS.SILKTypes.DetectionStruct
        )

        # Writers
        self.radar_report_writer = dds.DataWriter(
            self.participant.implicit_publisher, self.radar_report_topic
        )

        self.radar_report_data = DDS.SILKTypes.DetectionStruct

    def send_radar_report(self, range_m, azimuth_deg, zone_enum, zone_number):
        self.radar_report_data.Range = range_m
        self.radar_report_data.Azimuth = azimuth_deg
        self.radar_report_data.zoneTypeEnum = 1
        self.radar_report_data.ZoneNumber = zone_number

        self.radar_report_writer.write(self.radar_report_data)


if __name__ == "__main__":
    writer = ddsWriter()

    for _ in range(300):
        writer.send_radar_report(15, 21.4, 1, 1)
        print("hello")
        time.sleep(1)
