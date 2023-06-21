import time
import sys
import rti.connextdds as dds
from interfaces import DDS

#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
fireWeapon_topic = dds.Topic(participant, "FireWeapon", DDS.Weapon.FireWeapon)

#Writer
fireWeapon_writer = dds.DataWriter(participant.implicit_publisher, fireWeapon_topic)

#FireWeapon
fireWeapon_data = DDS.Weapon.FireWeapon
fireWeapon_data.fire = 1
fireWeapon_data.mode = 1

#Loop data sending
for count in range(10):
    try:
        print(f"Writing data, count {count}")

        #FireWeapon
        fireWeapon_writer.write(fireWeapon_data)

        time.sleep(1)

    except KeyboardInterrupt:
                break
