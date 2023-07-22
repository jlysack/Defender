#!/usr/bin/env python3

# hello_subscriber.py 
import rti.connextdds as dds 
import rti.asyncio 
from hello import HelloWorld 

participant = dds.DomainParticipant(domain_id=0) 

topic = dds.Topic(participant, 'HelloWorld Topic', HelloWorld) 

reader = dds.DataReader(participant.implicit_subscriber, topic) 

async def print_data(): 
    async for data in reader.take_data_async(): 
        print(f"Received: {data}") 
rti.asyncio.run(print_data() 
