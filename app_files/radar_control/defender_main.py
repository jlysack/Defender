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
import sys
import os
import Class
from Class.Configuration import SigProConfig, PlotConfig, BoardConfig
import radar_control
import rti.connextdds as dds
import rti.asyncio
import asyncio
from interfaces import DDS
from dds_listeners import ScanInstructionListener
import multiprocessing
from multiprocessing import Process
import time
 
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

def feet_to_m(feet):
    return feet * 0.3048

def m_to_feet(meters):
    return meters / 0.3048

async def get_scan_instruction(dds_listener):
    return await dds_listener.get_data()

async def main_execution_loop():
    dds_enabled = True

    # Initialize scan instruction listener
    dds_listener = ScanInstructionListener()

    # Setup Radar Control Configs
    radar_control_logger    = radar_control.init_rad_control_logger(True)
    plot_cfg                = radar_control.PlotConfig()
    #Brd                     = radar_control.configure_tinyrad()
    zone                    = 3
    previous_zone           = -1

    # Setup process queue
    radar_process = None
    process_queue = None 

    while True:
        # Wait for zone scan instruction
        scan_instruction = await get_scan_instruction(dds_listener)

        # Kill previous radar processes
        if radar_process is not None:
            process_queue.put(False)
            radar_process.join()


        # Pull zone number from message, ignore if invalid
        try:
            zone = int(scan_instruction.manualScanSetting)
        except (ValueError, TypeError) as error:
            print(error)
            sys.exit(1)

        if zone < 1 or zone > 3:
            print("Invalid zone number received, ignoring.")
        elif zone != previous_zone:
            print("Activating Stepper")
            time.sleep(1)
            print("Stepper moved")

            # TODO: INSERT STEPPER CODE HERE

            previous_zone = zone
        else:
            print("Commanded zone is same as current zone. Bypassing stepper activation.")

        # Check radiation enabled field
        if bool(scan_instruction.RadEnable) is False:
            print("Rad Enabled = False, radar disabled.")
            continue

        min_range = feet_to_m(const.ZONES[zone]['ADA_MIN_RANGE'])
        max_range = feet_to_m(const.ZONES[zone]['ADA_MAX_RANGE'])

        print(f"Zone {zone} - Minimum range: {min_range} m, Maximum range: {max_range} m")
        
        Brd = radar_control.configure_tinyrad()
        sigpro_cfg = SigProConfig(Brd, min_range, max_range, const.DEFAULT_NOISE_FLOOR, zone, dds_enabled) # ddsEnabled = False
        sigpro_cfg.logger = radar_control_logger

        process_queue = multiprocessing.Queue()
        radar_process = Process(target=radar_control.radar_search, args=(Brd, sigpro_cfg, plot_cfg, process_queue))
        radar_process.start()
    

if __name__ == "__main__":
    asyncio.run(main_execution_loop())
