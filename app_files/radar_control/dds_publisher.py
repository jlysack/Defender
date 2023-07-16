import time
import sys
import rti.connextdds as dds
from interfaces import DDS


class ddsWriter:
    # Participant
    participant = dds.DomainParticipant(domain_id=1)

    # Topics
    componentHealth_topic = dds.Topic(
        participant, "ComponentHealth", DDS.Metrics.ComponentHealth
    )
    objectInfo_topic = dds.Topic(participant, "ObjectInfo", DDS.Detection.ObjectInfo)
    detectionData_topic = dds.Topic(
        participant, "DetectionData", DDS.Detection.DetectionData
    )
    weaponInfo_topic = dds.Topic(participant, "WeaponInfo", DDS.Weapon.WeaponInfo)
    fireWeapon_topic = dds.Topic(participant, "FireWeapon", DDS.Weapon.FireWeapon)
    scanInstruction_topic = dds.Topic(
        participant, "ScanInstruction", DDS.Scanning.ScanInstruction
    )
    scanResponse_topic = dds.Topic(
        participant, "ScanResponse", DDS.Scanning.ScanResponse
    )
    trackData_topic = dds.Topic(participant, "TrackData", DDS.Tracking.TrackData)
    IFFRequest_topic = dds.Topic(participant, "IFFRequest", DDS.IFF.IFFRequest)
    IFFResponse_topic = dds.Topic(participant, "IFFResponse", DDS.IFF.IFFResponse)
    command_topic = dds.Topic(participant, "Command", DDS.misc.Command)
    radarSafety_topic = dds.Topic(participant, "RadarSafety", DDS.safety.RadarSafety)
    IRSafety_topic = dds.Topic(participant, "IRSafety", DDS.safety.IRSafety)

    # Writers
    componentHealth_writer = dds.DataWriter(
        participant.implicit_publisher, componentHealth_topic
    )
    objectInfo_writer = dds.DataWriter(participant.implicit_publisher, objectInfo_topic)
    detectionData_writer = dds.DataWriter(
        participant.implicit_publisher, detectionData_topic
    )
    weaponInfo_writer = dds.DataWriter(participant.implicit_publisher, weaponInfo_topic)
    fireWeapon_writer = dds.DataWriter(participant.implicit_publisher, fireWeapon_topic)
    scanInstruction_writer = dds.DataWriter(
        participant.implicit_publisher, scanInstruction_topic
    )
    scanResponse_writer = dds.DataWriter(
        participant.implicit_publisher, scanResponse_topic
    )
    trackData_writer = dds.DataWriter(participant.implicit_publisher, trackData_topic)
    IFFRequest_writer = dds.DataWriter(participant.implicit_publisher, IFFRequest_topic)
    IFFResponse_writer = dds.DataWriter(
        participant.implicit_publisher, IFFResponse_topic
    )
    command_writer = dds.DataWriter(participant.implicit_publisher, command_topic)
    radarSafety_writer = dds.DataWriter(
        participant.implicit_publisher, radarSafety_topic
    )
    IRSafety_writer = dds.DataWriter(participant.implicit_publisher, IRSafety_topic)

    # Creating data objects and filling

    # ComponentHealth
    componentHealth_data = DDS.Metrics.ComponentHealth
    componentHealth_data.Name = "JordanTestApp"
    componentHealth_data.State = 2

    # ObjectInfo
    objectInfo_data = DDS.Detection.ObjectInfo
    objectInfo_data.ObjectID = 111
    objectInfo_data.ZoneNumber = 1
    objectInfo_data.ZoneType = 1
    objectInfo_data.ObjectDirection = 1

    # DetectionData
    detectionData_data = DDS.Detection.DetectionData
    detectionData_data.TIN = 105
    detectionData_data.numberOfDetections = 100
    detectionData_data.dataArray = []  # No way this is right lol

    # WeaponInfo
    weaponInfo_data = DDS.Weapon.WeaponInfo
    weaponInfo_data.WeaponID = 1
    weaponInfo_data.State = 1
    weaponInfo_data.PowerReadout = 1111

    # FireWeapon
    fireWeapon_data = DDS.Weapon.FireWeapon
    fireWeapon_data.fire = 1
    fireWeapon_data.mode = 1

    # ScanInstruction - Can write it as a 1 liner or assign things after, or mix.
    # scanInstruction_data = DDS.Scanning.ScanInstruction(radarSetting = 1, manualScanSetting = 2)
    scanInstruction_data = DDS.Scanning.ScanInstruction
    scanInstruction_data.radarSetting = 1
    scanInstruction_data.manualScanSetting = 1

    # ScanResponse
    scanResponse_data = DDS.Scanning.ScanResponse
    scanResponse_data.ZoneNumber = 3

    # TrackData
    trackData_data = DDS.Tracking.TrackData
    trackData_data.ObjectID = 111
    trackData_data.Coordinates = "51.241 -2.141"

    # IFFRequest
    IFFRequest_data = DDS.IFF.IFFRequest
    IFFRequest_data.RequestID = 1
    IFFRequest_data.Request = "Sending from python Test app"

    # IFFResponse
    IFFResponse_data = DDS.IFF.IFFResponse
    IFFResponse_data.ObjectIdentity = 2

    # Command
    command_data = DDS.misc.Command
    command_data.Source = "Python test app"
    command_data.Destination = "nothing"
    command_data.Command = "Explode the drone lol"

    # RadarSafety
    radarSafety_data = DDS.safety.RadarSafety
    radarSafety_data.enabled = 1

    # IRSafety
    IRSafety_data = DDS.safety.IRSafety
    IRSafety_data.enabled = 1

    # Loop data sending
    for count in range(1000):
        # Catch control-C interrupt
        try:
            # Print counter
            print(f"Writing data, count {count}")

            # Write the data

            # ComponentHealth
            componentHealth_writer.write(componentHealth_data)
            # ObjectInfo
            objectInfo_writer.write(objectInfo_data)
            # DetectionData
            detectionData_writer.write(detectionData_data)
            # WeaponInfo
            weaponInfo_writer.write(weaponInfo_data)
            # FireWeapon
            fireWeapon_writer.write(fireWeapon_data)
            # ScanInstruction
            scanInstruction_writer.write(scanInstruction_data)
            # ScanResponse
            scanResponse_writer.write(scanResponse_data)
            # TrackData
            trackData_writer.write(trackData_data)
            # IFFRequest
            IFFRequest_writer.write(IFFRequest_data)
            # IFFResponse
            IFFResponse_writer.write(IFFResponse_data)
            # Command
            command_writer.write(command_data)
            # RadarSafety
            radarSafety_writer.write(radarSafety_data)
            # IRSafety
            IRSafety_writer.write(IRSafety_data)

            # sleep
            time.sleep(1)
            # Catch control-C interrupt
        except KeyboardInterrupt:
            break
