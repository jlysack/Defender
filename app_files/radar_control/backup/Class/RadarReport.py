#!/usr/bin/python3
import sys
sys.path.append("../")
import rti.connextdds as dds
from interfaces import DDS

class RadarReportWriter:

    def __init__(self):
        # Participant
        self.participant = dds.DomainParticipant(domain_id=1)

        # Topics
        self.radar_report_topic = dds.Topic(self.participant, "RadarReport", DDS.Tracking.RadarReport)

        # Writers
        self.radar_report_writer = dds.DataWriter(self.participant.implicit_publisher, self.radar_report_topic)

        # Initialize data
        self.radar_report_data = DDS.Tracking.RadarReport

    def send(self, range_m, azimuth_deg, zone_number, engagement_zone_flag): #, amplitude, zone_enum, zone_number):
        # Set data
        self.radar_report_data.Range              = range_m
        self.radar_report_data.Azimuth            = azimuth_deg
        self.radar_report_data.ZoneNumber         = zone_number
        self.radar_report_data.EngagementZoneFlag = engagement_zone_flag

        # Publish data
        self.radar_report_writer.write(self.radar_report_data)
