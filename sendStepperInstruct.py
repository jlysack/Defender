import time
import sys
import rti.connextdds as dds
from interfaces import DDS

class ddsWriter:

    #Participant
    participant = dds.DomainParticipant(domain_id=1)

    #Topics
    scanInstruction_topic = dds.Topic(participant, "ScanInstruction", DDS.Scanning.ScanInstruction)

    #Writers
    scanInstruction_writer = dds.DataWriter(participant.implicit_publisher, scanInstruction_topic)  

    #Creating data objects and filling

    #userinput = input("zone?: ")

    #ScanInstruction - Can write it as a 1 liner or assign things after, or mix.
    #scanInstruction_data = DDS.Scanning.ScanInstruction(radarSetting = 1, manualScanSetting = 2)
    scanInstruction_data = DDS.Scanning.ScanInstruction
    scanInstruction_data.radarSetting = 1
    scanInstruction_data.manualScanSetting = 3 #Change this to 1 2 or 3 and restart the code!

    #Loop data sending
    for count in range(2):
            # Catch control-C interrupt
            try:
                #Print counter
                print(f"Writing data, count {count}")

                #Write the data

                #ScanInstruction
                scanInstruction_writer.write(scanInstruction_data)
               
                #sleep
                time.sleep(1)
                #Catch control-C interrupt
            except KeyboardInterrupt:
                break
