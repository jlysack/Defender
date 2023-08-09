#!/usr/bin/env python3

import rti.connextdds as dds
import rti.asyncio
import asyncio
from interfaces import DDS

participant = dds.DomainParticipant(domain_id=1)

radar_report_topic = dds.Topic(participant, "RadarReport", DDS.Tracking.RadarReport)
reader = dds.DataReader(participant.implicit_subscriber, radar_report_topic)
writer = dds.DataWriter(participant.implicit_publisher, radar_report_topic)

RadarReport_ReceivedData = DDS.Tracking.RadarReport

async def print_data():
    async for data in reader.take_data_async():
        print(f"Received: {data}")

        RadarReport_ReceivedData = data

        writer.write(RadarReport_ReceivedData)

    await asyncio.sleep(0.5)

        

async def main_loop():
    print("main loop")

    await asyncio.sleep(1)


async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(print_data())
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())  

rti.asyncio.run(print_data())
