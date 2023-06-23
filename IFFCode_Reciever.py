import time
import sys
import rti.connextdds as dds
import rti.asyncio
import asyncio
import aiofiles
from interfaces import DDS

participant = dds.DomainParticipant(domain_id=1)
IFFCode_topic = dds.Topic(participant, "IFFCode", DDS.IFF.SetCode)
IFFCode_reader = dds.DataReader(participant.implicit_subscriber, IFFCode_topic)
IFFCode_ReceivedData = DDS.IFF.SetCode


async def print_data():
    while True:
        async for data in IFFCode_reader.take_data_async():
            print(f"Received: {data}")


async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(print_data()),
    ]
    await asyncio.gather(*tasks)

asyncio.run(run_event_loop())
