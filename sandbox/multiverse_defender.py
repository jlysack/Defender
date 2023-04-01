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
import constants_v2 as const
import sys
import os
 
def print_zone_info(zone):
    for field in const.ZONES[zone]:
        print(field + ': ' + str(const.ZONES[zone][field]))

def process_detections(detections, zone):
    # For a given Python list of detection objects and the current zone being
    # searched, return a filtered Python list of detection objects with only 
    # detections in the zone being searched

    # detections:   Python list of Detection objects, LOCAL coordinates
    # zone:         integer number of the current zone being searched
 
    filtered_dets = []

    try:
        assert(type(zone) == int)
    except:
        print("poop")
        sys.exit(0)

    # Loop through each detection, filter out non-ADA detections, and set flags
    for det in detections:
        processed_det.flags = compute_detection_flags(det, zone)
        if True in processed_det.flags:
            filtered_dets.append(processed_det)
 
    return filtered_dets
 
def compute_detection_flags(detection, zone):
    flags = {
        1: (False, False),
        2: (False, False),
        3: (False, False)
    }

    ada_min_range = const.ZONES[zone]['ADA_MIN_RANGE']
    ada_max_range = const.ZONES[zone]['ADA_MAX_RANGE']
    ez_min_range  = const.ZONES[zone]['EZ_MIN_RANGE']
    ez_max_range  = const.ZONES[zone]['EZ_MAX_RANGE']
 
    ada_min_az = const.LOCAL_ZONE_PARAMS['ADA_MIN_AZ'] 
    ada_max_az = const.LOCAL_ZONE_PARAMS['ADA_MAX_AZ'] 
    ez_min_az  = const.LOCAL_ZONE_PARAMS['EZ_MIN_AZ'] 
    ez_max_az  = const.LOCAL_ZONE_PARAMS['EZ_MAX_AZ'] 
    min_el     = const.LOCAL_ZONE_PARAMS['MIN_EL'] 
    max_el     = const.LOCAL_ZONE_PARAMS['MAX_EL'] 
 
    # Check elevation first, since it is common between ADA/EZ
    if detection.el <= max_el and detection.el >= min_el:

        # Check if detection is in engagement zone (inclusive of ADA)
        if  detection.range <= ez_max_range and detection.range >= ez_min_range and  \
            detection.az    <= ez_max_az    and detection.az    >= ez_min_az:
       
            flags[zone] = (True, True)
 
        # Check if detection is in Air Defense Area but NOT engagement zone
        elif detection.range <= ada_max_range and detection.range >= ada_min_range and  \
             detection.az    <= ada_max_az    and detection.az    >= ada_min_az:
       
            flags[zone] = (True, False)

if __name__ == "__main__":
    break
