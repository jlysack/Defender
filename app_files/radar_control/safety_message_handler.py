#!/usr/bin/env python3

import rti.connextdds as dds
import rti.asyncio
from interfaces import DDS

participant = dds.DomainParticipant(domain_id=1)

topic = dds.Topic(participant, "RadarSafety", DDS.safety.RadarSafety)

reader = dds.DataReader(participant.implicit_subscriber, topic)

async def print_data():

    async for data in reader.take_data_async():
        print(f"Received: {data}")

rti.asyncio.run(print_data())
