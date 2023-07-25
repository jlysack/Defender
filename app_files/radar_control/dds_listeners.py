#!/usr/bin/env python3

import rti.connextdds as dds
import rti.asyncio
from interfaces import DDS

class ScanInstructionListener:
    def __init__(self):
        self.participant = dds.DomainParticipant(domain_id=1)

        self.topic = dds.Topic(self.participant, "ScanInstruction", DDS.Scanning.ScanInstruction)

        self.reader = dds.DataReader(self.participant.implicit_subscriber, self.topic)

    async def get_data(self):
        async for data in self.reader.take_data_async():
            return data
