import time
import sys
import rti.connextdds as dds
from interfaces import DDS


#Participant
participant = dds.DomainParticipant(domain_id=1)

publisher_qos = dds.QosProvider.default.publisher_qos
fireWeapon_Publisher = dds.Publisher(participant, publisher_qos)
datawriter_qos = dds.QosProvider.default.datawriter_qos

#Topics
componentHealth_topic  = dds.Topic(participant, "ComponentHealth", DDS.Metrics.ComponentHealth)

#Writer
#Just added this dynamic data thing not sure if thats a thing we can use?
componentHealth_writer  = dds.DataWriter(fireWeapon_Publisher, componentHealth_topic, datawriter_qos)

componentHealth_data = DDS.Metrics.ComponentHealth
componentHealth_data.Name = "TestingQOS"
componentHealth_data.State = 1

#Loop data sending
for count in range(1000):
    try:
        print(f"Writing data, count {count}")

        #Send
        componentHealth_writer.write(componentHealth_data)
        

        time.sleep(1)

    except KeyboardInterrupt:
                break