import time
import sys
import rti.connextdds as dds
from interfaces import DDS

class ddsWriter:
    #Participant
    participant = dds.DomainParticipant(domain_id=1)

    # Topics
    Command_topic = dds.Topic(participant, "DDS_misc", DDS.misc.Command)

    # Reader
    Command_Writer = dds.DataWriter(participant.implicit_publisher, Command_topic)  


    #Command
    Command_data = DDS.misc.Command
    Command_data.Command = "None"

    #Loop data sending
    for count in range(1):
            # Catch control-C interrupt
            try:
                #Print counter
                print(f"Writing data, count {count}")

                #Write the data

                #ScanInstruction
                Command_Writer.write(Command_data)
                #Command_data.Command = "message2"
                #Command_Writer.write(Command_data)
                #sleep
                time.sleep(1)
                #Catch control-C interrupt
            except KeyboardInterrupt:
                break

