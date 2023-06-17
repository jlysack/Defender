#!/usr/bin/python3
import sys
sys.path.append("../")
try:
    import rti.connextdds as dds
    from interfaces import DDS
except ModuleNotFoundError:
    pass

class RadarReportWriter:

    def __init__(self):
        # Participant
        self.participant = dds.DomainParticipant(domain_id=1)

        # Topics
        self.radar_report_topic = dds.Topic(self.participant, "RadarReport", DDS.SILKTypes.DetectionStruct)

        # Writers
        self.radar_report_writer = dds.DataWriter(self.participant.implicit_publisher, self.radar_report_topic)

        # Initialize data
        self.radar_report_data = DDS.SILKTypes.DetectionStruct

    def send(self, range_m, azimuth_deg): #, amplitude, zone_enum, zone_number):
        # Set data
        self.radar_report_data.Range        = range_m
        self.radar_report_data.Azimuth      = azimuth_deg
        self.radar_report_data.zoneTypeEnum = DDS.SILKTypes.ZoneType.EngagementZone 
        self.radar_report_data.ZoneNumber   = 0

        # TODO: Add later when we can change the file
        #self.radar_report_data.Amplitude = amplitude_db
        #self.radar_report_data.EngagementZoneFlag = engagement_zone_flag 


        # Publish data
        self.radar_report_writer.write(self.radar_report_data)
