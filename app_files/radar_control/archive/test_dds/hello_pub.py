#!/usr/bin/env python3

# hello_publisher.py 
import time 
import rti.connextdds as dds 
from hello import HelloWorld 

participant = dds.DomainParticipant(domain_id=0) 

topic = dds.Topic(participant, 'HelloWorld Topic', HelloWorld) 

writer = dds.DataWriter(participant.implicit_publisher, topic) 

for i in range(10): 
    writer.write(HelloWorld(message=f'Hello World! #{i}')) 
    time.sleep(1) 
