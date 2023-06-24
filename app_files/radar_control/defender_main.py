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

            # TODO: INSERT STEPPER CODE HERE and remove simulated sleep above

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
