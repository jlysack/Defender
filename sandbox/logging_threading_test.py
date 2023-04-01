#!/usr/bin/env python3
import logging
import time
import os
import multiprocessing
from multiprocessing import Process
import threading
from datetime import datetime

def setup_logger():
    # Get current Python filename
    app_name = str(os.path.basename(__file__)).strip('.py')

    # Create the logger and set its default level
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to DEBUG
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARN)

    # create file handler and set level to DEBUG
    now = str(datetime.now().strftime('%Y%m%d_%H%M%S'))
    file_handler = logging.FileHandler(filename = str(app_name + '_' + now + '.log')) 
    file_handler.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s: %(name)s - %(threadName)s - %(levelname)s: %(message)s')

    # add formatters to our handlers
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # add Handlers to our logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # return the logger for future use
    return logger

def transmit():
    logger.info("Transmiting RF")
    logger.info("RF Data Received\n")

def move_motors():
    logger.info("Actuating motors")
    logger.info("Motors in position\n")

def process_data():
    logger.info("Processing telemetry data\n")
    logger.info("Telemetry data processed\n")

def send_external_report():
    logger.info("Sending detection report externally\n")
    logger.info("Detection report sent")

if __name__ == '__main__':
    logger = setup_logger()

    # Multithreading
    mt_start_time = time.time()

    for i in range(500):
        motor_thread = threading.Thread(target = move_motors)
        tinyrad_thread = threading.Thread(target = transmit)
        message_thread = threading.Thread(target = send_external_report)

        motor_thread.name = 'motor_thread'
        tinyrad_thread.name = 'tinyrad_thread'
        message_thread.name = 'msg_thread'

        motor_thread.start()
        motor_thread.join()

        tinyrad_thread.start()
        tinyrad_thread.join()

        logger.info("Processing telemetry data\n")
        logger.info("Telemetry data processed\n")

        message_thread.start()


    mt_end_time = time.time()

    # Multiprocessing
    mp_start_time = time.time()

    for i in range(500):
        motor_proc = Process(target=move_motors) 
        tinyrad_proc = Process(target=transmit) 
        msg_proc = Process(target=send_external_report) 

        motor_proc.start()
        motor_proc.join()

        tinyrad_proc.start()
        tinyrad_proc.join()

        logger.info("Processing telemetry data\n")
        logger.info("Telemetry data processed\n")

        msg_proc.start()


    time.sleep(2)
    mp_end_time = time.time()

    # get the execution time
    mt_elapsed_time = mt_end_time - mt_start_time
    logger.warning('Multithreading execution time: ' + str(mt_elapsed_time) + ' seconds')
    mp_elapsed_time = mp_end_time - mp_start_time
    logger.warning('Multiprocessing execution time: ' + str(mp_elapsed_time) + ' seconds')
