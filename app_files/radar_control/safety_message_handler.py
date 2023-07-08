#!/usr/bin/env python3

import os
import rti.connextdds as dds
import rti.asyncio
from interfaces import DDS

participant = dds.DomainParticipant(domain_id=1)

topic = dds.Topic(participant, "RadarSafety", DDS.safety.RadarSafety)

reader = dds.DataReader(participant.implicit_subscriber, topic)

async def print_data():
    async for data in reader.take_data_async():
        # Write to file or queue or whatever
        print(f"Received: {data}")

async def handle_messages(process_queue, debug=True):
    async for data in reader.take_data_async():
        process_queue.put(data.enabled)
        print(data.enabled)

async def listen_for_messages(f):
    async for data in reader.take_data_async():
        with open('/tmp/.radar_safety.txt', 'w') as f:
            f.write(str(int(data.enabled)))


if __name__ == "__main__":
    with open('/tmp/.radar_safety.txt', 'w') as f:
        f.write(str(1)) # Initialize radar_safety to enabled
    try:
        rti.asyncio.run(listen_for_messages(f))
    except Exception as e:
        print(e)
