#!/usr/bin/env python3

# Radar Search Mode
#   Align Boresight
#       Check Motor Preconditions (time elapsed)
#       Actuate Stepper Motor
#   Obtain Sensor Data
#       Call TinyRad Functions to Obtain Sensor Data
#       Reformat Data (organize variable structure)
#   Process Telemetry Data
#       Filter Detections (not in any zone)
#       Set Flags
#   Report Detections
#       Populate Message
#       Send Message
 
# Getters/Setters versus Properties
# Case usage (camelcase or underscores?)
#
import constants as const
 
def process_telemetry_data(detections, current_zone):
    # detections:   Python list of Detection objects
    # zone:         integer number of the current zone being searched
 
    for det in detections:
        for zone in const.ZONES:
            if detection_in_zone(det, zone):
                pass
 
    az_offset = const.BORESIGHT_OFFSET[zone]
 
    for det in detections:
        det_az  = det.azimuth + az_offset
        det_rng = det.range
 
   
 
    return dets_filtered
 
def set_detection_flags(detection, zone):
    ez_min_range  = const.EZ_MIN_RANGE[zone]
    ez_max_range  = const.EZ_MAX_RANGE[zone]
    ez_min_az     = const.EZ_MIN_AZ[zone]
    ez_max_az     = const.EZ_MAX_AZ[zone]
    ez_min_el     = const.EZ_MIN_EL[zone]
    ez_max_el     = const.EZ_MAX_EL[zone]
 
    ada_min_range  = const.ADA_MIN_RANGE[zone]
    ada_max_range  = const.ADA_MAX_RANGE[zone]
    ada_min_az     = const.ADA_MIN_AZ[zone]
    ada_max_az     = const.ADA_MAX_AZ[zone]
    ada_min_el     = const.ADA_MIN_EL[zone]
    ada_max_el     = const.ADA_MAX_EL[zone]
 
    # Check if detection is in engagement zone (inclusive of ADA)
    if  detection.range <= ez_max_range and detection.range >= ez_min_range and  \
        detection.az    <= ez_max_az    and detection.az    >= ez_min_az    and  \
        detection.el    <= ez_max_el    and detection.el    >= ez_min_el:
       
        return (True, True)
 
    # Check if detection is in Air Defense Area but NOT engagement zone
    elif detection.range <= ada_max_range and detection.range >= ada_min_range and  \
         detection.az    <= ada_max_az    and detection.az    >= ada_min_az    and  \
         detection.el    <= ada_max_el    and detection.el    >= ada_min_el:
       
        return (True, False)

    # Detection is not in Air Defense Area
    return (False, False)
