#!/usr/bin/env python3

import subprocess as sp
import constants as const
import sys
import os
import Class
from Class.Configuration import SigProConfig, PlotConfig, BoardConfig
import radar_control
import safety_message_handler
import rti.connextdds as dds
import rti.asyncio
import asyncio
from interfaces import DDS
from dds_listeners import ScanInstructionListener
import multiprocessing
from multiprocessing import Process
import time
import threading
 
def print_zone_info(zone):
    for field in const.ZONES[zone]:
        print(field + ': ' + str(const.ZONES[zone][field]))

def feet_to_m(feet):
    return feet * 0.3048

def m_to_feet(meters):
    return meters / 0.3048

async def get_scan_instruction(dds_listener):
    return await dds_listener.get_data()

async def main_execution_loop(health_message_writer):
    dds_enabled = True
    debug_enabled = False

    # Initialize scan instruction listener
    dds_listener = ScanInstructionListener()

    # Setup Radar Control Configs
    logger          = radar_control.init_rad_control_logger(debug_enabled)
    plot_cfg        = radar_control.PlotConfig()
    zone            = 3
    previous_zone   = -1

    # Initialize radar_process to None
    radar_process = None

    # Create process queue to be able to cancel/terminate execution of radar_search safely
    process_queue = multiprocessing.Queue()

    try:
        while True:
            # Wait for zone scan instruction
            # NOTE: execution pauses here until a message is received
            scan_instruction = await get_scan_instruction(dds_listener)

            # Once we receive scan instruction, 
            # Kill previous radar processes using process_queue (killed in radar_control.radar_search)
            if radar_process is not None:
                process_queue.put(False)
                radar_process.join()

            # Pull zone number from message
            try:
                zone = int(scan_instruction.manualScanSetting)
            except (ValueError, TypeError) as error:
                logger.error(error)
                sys.exit(1)

            # Ignore zone if invalid
            if zone < 1 or zone > 3:
                logger.warn("Invalid zone number received, ignoring.")
            # If commanded zone differs from current/previous, activate stepper 
            elif zone != previous_zone:
                DELAY = 2 # seconds
                logger.info(f"Delaying {DELAY} seconds for stepper movement.")
                time.sleep(DELAY)
                previous_zone = zone
            # If commanded zone is same as current/previous, do nothing
            else:
                logger.info("Commanded zone is same as current zone. Bypassing stepper activation.")

            # Check radiation enabled field - if set to False, continue to next loop
            # iteration without starting the radar_search process. Stepper motor will
            # move, but radiation will not be enabled
            # NOTE: radar_control.check_radar_safety_file() checks the /tmp/.radar_safety.txt file
            #       if running into issues here, check the file and/or permissions on the directory
            if radar_control.check_radar_safety_file() == "0":
                logger.info("Radiation Disabled via Safety Toggle. Resend Scan Instruction after enabling radiation safety toggle.")
                continue

            # Set min and max range according to zone parameters
            min_range = feet_to_m(const.ZONES[zone]['ADA_MIN_RANGE'])
            max_range = feet_to_m(const.ZONES[zone]['ADA_MAX_RANGE'])
            logger.info(f"Zone {zone} - Minimum range: {min_range} m, Maximum range: {max_range} m")
            
            # Instantiate TinyRad and sigpro_cfg objects
            Brd = radar_control.configure_tinyrad()
            sigpro_cfg = SigProConfig(Brd, min_range, max_range, const.DEFAULT_NOISE_FLOOR, zone, dds_enabled)
            sigpro_cfg.logger = logger

            # Create process queue to be able to cancel/terminate execution of radar_search safely
            process_queue = multiprocessing.Queue()

            # Create and start process for radar_search, then return to the top to listen for the next scan instruction
            radar_process = Process(target=radar_control.radar_search, args=(Brd, sigpro_cfg, plot_cfg, process_queue))
            radar_process.start()

            # Send health message
            
            send_health_message(health_message_writer, time.time(), 1)

    except KeyboardInterrupt:
        print("Ctrl+C Detected in defender_main.py main_execution_loop()")
        sys.exit(0)

def send_health_message(writer, time, state=1):
    global saved_time

    if time - saved_time >= 10.0:
        componentHealth_data = DDS.Metrics.ComponentHealth
        componentHealth_data.Name = "TA_R"
        componentHealth_data.State = state

        writer.write(componentHealth_data)
        saved_time = time

    print("Inside send_health_message")
    return True
    

if __name__ == "__main__":
    global saved_time
    saved_time = time.time()

    participant = dds.DomainParticipant(domain_id=1)

    # Topic
    health_message_topic = dds.Topic(participant, "ComponentHealth", DDS.Metrics.ComponentHealth)

    # Writer
    health_message_writer = dds.DataWriter(participant.implicit_publisher, health_message_topic)

    try:
        safety_process = sp.Popen('./safety_message_handler.py')
        asyncio.run(main_execution_loop(health_message_writer))
    except KeyboardInterrupt:
        print("Ctrl+C Detected in defender_main.py __main__(). Exiting.")
        # Kill health_message writer
        #health_message_timer.cancel()
        # write a 0
        send_health_message(health_message_writer, 0)
        sys.exit(0)
    except Exception as e:
        print(e)
        # Kill health_message writer
        #health_message_timer.cancel()
        # write a 0
        send_health_message(health_message_writer, 0)
        sys.exit(0)
