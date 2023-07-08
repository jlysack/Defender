
# WARNING: THIS FILE IS AUTO-GENERATED. DO NOT MODIFY.

# This file was generated from interfaces.idl
# using RTI Code Generator (rtiddsgen) version 4.0.0.
# The rtiddsgen tool is part of the RTI Connext DDS distribution.
# For more information, type 'rtiddsgen -help' at a command shell
# or consult the Code Generator User's Manual.

from dataclasses import field
from typing import Union, Sequence, Optional
import rti.idl as idl
from enum import IntEnum


DDS = idl.get_module("DDS")

DDS_SILKTypes = idl.get_module("DDS_SILKTypes")

DDS.SILKTypes = DDS_SILKTypes

@idl.enum
class DDS_SILKTypes_ComponentStatus(IntEnum):
    Offline = 0
    Online = 1
    Hit = 2

DDS.SILKTypes.ComponentStatus = DDS_SILKTypes_ComponentStatus

@idl.enum
class DDS_SILKTypes_ZoneType(IntEnum):
    DefenseZone = 0
    EngagementZone = 1
    SafeZone = 2

DDS.SILKTypes.ZoneType = DDS_SILKTypes_ZoneType

@idl.enum
class DDS_SILKTypes_ObjectAction(IntEnum):
    Entered = 0
    Exited = 1

DDS.SILKTypes.ObjectAction = DDS_SILKTypes_ObjectAction

@idl.enum
class DDS_SILKTypes_ObjectIdentity(IntEnum):
    Unknown = 0
    Friendly = 1
    Enemy = 2

DDS.SILKTypes.ObjectIdentity = DDS_SILKTypes_ObjectIdentity

@idl.enum
class DDS_SILKTypes_ScannerState(IntEnum):
    Unknown = 0
    Scanning = 1
    Ready = 2
    Error = 3

DDS.SILKTypes.ScannerState = DDS_SILKTypes_ScannerState

@idl.enum
class DDS_SILKTypes_WeaponState(IntEnum):
    Unknown = 0
    Ready = 1
    Firing = 2
    Error = 3

DDS.SILKTypes.WeaponState = DDS_SILKTypes_WeaponState

@idl.struct
class DDS_SILKTypes_CartesianCoordinates:
    x: idl.float32 = 0.0
    y: idl.float32 = 0.0
    z: idl.float32 = 0.0

DDS.SILKTypes.CartesianCoordinates = DDS_SILKTypes_CartesianCoordinates

@idl.enum
class DDS_SILKTypes_radarMode(IntEnum):
    AI = 0
    Manual = 1

DDS.SILKTypes.radarMode = DDS_SILKTypes_radarMode

@idl.enum
class DDS_SILKTypes_scanState(IntEnum):
    Sweep = 0
    zone1 = 1
    zone2 = 2
    zone3 = 3

DDS.SILKTypes.scanState = DDS_SILKTypes_scanState

@idl.struct
class DDS_SILKTypes_DetectionStruct:
    Range: idl.float32 = 0.0
    Azimuth: idl.float32 = 0.0
    zoneTypeEnum: DDS.SILKTypes.ZoneType = DDS.SILKTypes.ZoneType.DefenseZone
    ZoneNumber: idl.int32 = 0

DDS.SILKTypes.DetectionStruct = DDS_SILKTypes_DetectionStruct

DDS_Metrics = idl.get_module("DDS_Metrics")

DDS.Metrics = DDS_Metrics

@idl.struct(
    member_annotations = {
        'Name': [idl.key, idl.bound(100)],
    }
)
class DDS_Metrics_ComponentHealth:
    Name: str = ""
    State: DDS.SILKTypes.ComponentStatus = DDS.SILKTypes.ComponentStatus.Offline

DDS.Metrics.ComponentHealth = DDS_Metrics_ComponentHealth

DDS_Detection = idl.get_module("DDS_Detection")

DDS.Detection = DDS_Detection

@idl.struct
class DDS_Detection_ObjectInfo:
    ObjectID: Optional[idl.int32] = None
    ZoneNumber: idl.int32 = 0
    ZoneType: DDS.SILKTypes.ZoneType = DDS.SILKTypes.ZoneType.DefenseZone
    ObjectDirection: DDS.SILKTypes.ObjectAction = DDS.SILKTypes.ObjectAction.Entered

DDS.Detection.ObjectInfo = DDS_Detection_ObjectInfo

@idl.struct(
    member_annotations = {
        'TIN': [idl.key, ],
        'dataArray': [idl.bound(20)],
    }
)
class DDS_Detection_DetectionData:
    TIN: idl.int32 = 0
    numberOfDetections: idl.int32 = 0
    dataArray: Sequence[DDS.SILKTypes.DetectionStruct] = field(default_factory = list)

DDS.Detection.DetectionData = DDS_Detection_DetectionData

DDS_Weapon = idl.get_module("DDS_Weapon")

DDS.Weapon = DDS_Weapon

@idl.struct
class DDS_Weapon_WeaponInfo:
    WeaponID: idl.int32 = 0
    State: DDS.SILKTypes.WeaponState = DDS.SILKTypes.WeaponState.Unknown
    PowerReadout: idl.float32 = 0.0

DDS.Weapon.WeaponInfo = DDS_Weapon_WeaponInfo

@idl.struct
class DDS_Weapon_FireWeapon:
    fire: bool = False
    mode: Optional[idl.int32] = None

DDS.Weapon.FireWeapon = DDS_Weapon_FireWeapon

DDS_Scanning = idl.get_module("DDS_Scanning")

DDS.Scanning = DDS_Scanning

@idl.struct
class DDS_Scanning_ScanInstruction:
    radarSetting: DDS.SILKTypes.radarMode = DDS.SILKTypes.radarMode.AI
    manualScanSetting: DDS.SILKTypes.scanState = DDS.SILKTypes.scanState.Sweep
    RadEnable: bool = False

DDS.Scanning.ScanInstruction = DDS_Scanning_ScanInstruction

@idl.struct
class DDS_Scanning_ScanResponse:
    ZoneNumber: idl.int32 = 0

DDS.Scanning.ScanResponse = DDS_Scanning_ScanResponse

DDS_Tracking = idl.get_module("DDS_Tracking")

DDS.Tracking = DDS_Tracking

@idl.struct(
    member_annotations = {
        'Coordinates': [idl.bound(100)],
    }
)
class DDS_Tracking_TrackData:
    ObjectID: Optional[idl.int32] = None
    Coordinates: str = ""
    CartesianCoordinate: Optional[DDS.SILKTypes.CartesianCoordinates] = None

DDS.Tracking.TrackData = DDS_Tracking_TrackData

@idl.struct
class DDS_Tracking_RadarReport:
    Range: idl.float32 = 0
    Azimuth: idl.float32 = 0
    ZoneNumber: idl.int32 = 0
    EngagementZoneFlag: bool = False

DDS.Tracking.RadarReport = DDS_Tracking_RadarReport

DDS_IFF = idl.get_module("DDS_IFF")

DDS.IFF = DDS_IFF

@idl.struct(
    member_annotations = {
        'Request': [idl.bound(100)],
    }
)
class DDS_IFF_IFFRequest:
    RequestID: idl.int32 = 0
    Request: str = ""

DDS.IFF.IFFRequest = DDS_IFF_IFFRequest

@idl.struct
class DDS_IFF_IFFResponse:
    ObjectIdentity: DDS.SILKTypes.ObjectIdentity = DDS.SILKTypes.ObjectIdentity.Unknown

DDS.IFF.IFFResponse = DDS_IFF_IFFResponse

@idl.struct
class DDS_IFF_SetCode:
    IFFCode: DDS.SILKTypes.ObjectIdentity = DDS.SILKTypes.ObjectIdentity.Unknown

DDS.IFF.SetCode = DDS_IFF_SetCode

@idl.struct
class DDS_IFF_RequestIFF_UAV:
    RequestID: idl.int32 = 0

DDS.IFF.RequestIFF_UAV = DDS_IFF_RequestIFF_UAV

@idl.struct
class DDS_IFF_ResponseIFF_UAV:
    ObjectIdentity: DDS.SILKTypes.ObjectIdentity = DDS.SILKTypes.ObjectIdentity.Unknown

DDS.IFF.ResponseIFF_UAV = DDS_IFF_ResponseIFF_UAV

DDS_misc = idl.get_module("DDS_misc")

DDS.misc = DDS_misc

@idl.struct(
    member_annotations = {
        'Source': [idl.bound(100)],
        'Destination': [idl.bound(100)],
        'Command': [idl.bound(100)],
    }
)
class DDS_misc_Command:
    Source: str = ""
    Destination: str = ""
    Command: str = ""

DDS.misc.Command = DDS_misc_Command

DDS_safety = idl.get_module("DDS_safety")

DDS.safety = DDS_safety

@idl.struct
class DDS_safety_RadarSafety:
    enabled: bool = False

DDS.safety.RadarSafety = DDS_safety_RadarSafety

@idl.struct
class DDS_safety_IRSafety:
    enabled: bool = False

DDS.safety.IRSafety = DDS_safety_IRSafety
