#!/usr/bin/env python3

import time
import sys
import rti.connextdds as dds
from interfaces import DDS


class ddsWriter:
    # Participant
    participant = dds.DomainParticipant(domain_id=1)

    # Topics
    responseIFF_topic = dds.Topic(participant, "IFFResponse", DDS.IFF.IFFResponse)

    # Writers
    responseIFF_writer = dds.DataWriter(
        participant.implicit_publisher, responseIFF_topic
    )

    responseIFF_data = DDS.IFF.IFFResponse
    responseIFF_data.ObjectIdentity = 0

    # Loop data sending
    for count in range(2):
        # Catch control-C interrupt
        try:
            # Print counter
            print(f"Writing data, count {count}")

            # Write the data

            # ScanInstruction
            responseIFF_writer.write(responseIFF_data)

            # sleep
            time.sleep(1)
            # Catch control-C interrupt
        except KeyboardInterrupt:
            break
