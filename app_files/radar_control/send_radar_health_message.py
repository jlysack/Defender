#!/usr/bin/python3

import time
import sys
import rti.connextdds as dds
from interfaces import DDS


if __name__ == "__main__":

    # Participant
    participant = dds.DomainParticipant(domain_id=1)

    # Topics
    radarHealth_topic = dds.Topic(participant, "ComponentHealth", DDS.Metrics.ComponentHealth)

    # Writers
    radarHealth_writer = dds.DataWriter(participant.implicit_publisher, radarHealth_topic)

    # Data
    radarHealth_data = DDS.Metrics.ComponentHealth
    radarHealth_data.Name = "TA_R"
    radarHealth_data.State = 1

    #Loop data sending
    while True:
        # Catch control-C interrupt
        try:
            radarHealth_writer.write(radarHealth_data)
            time.sleep(1)
        #Catch control-C interrupt
        except KeyboardInterrupt:
            break
