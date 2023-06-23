#!/usr/bin/python3

from datetime import datetime
import logging
import sys, os
sys.path.append("../")
import Class.TinyRad as TinyRad
from Class.Configuration import SigProConfig, PlotConfig, BoardConfig
import numpy as np
import matplotlib.pyplot as plt
import signal
import argparse

# NOTE: This function will need to be called in the defender_main.py function
def init_rad_control_logger(debug_enabled = False):
    # Get current Python filename
    app_name = str(os.path.basename(__file__)).strip('.py')

    # Create the logger
    logger = logging.getLogger(app_name)

    # Create console handler 
    stream_handler = logging.StreamHandler()

    # Create file handler 
    now = str(datetime.now().strftime('%Y%m%d_%H%M%S'))
    file_handler = logging.FileHandler(filename = str('logs/' + app_name + '_' + now + '.log'))

    # Set default logging levels for logger, console handler and file handler
    logger.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    
    if debug_enabled is True:
        stream_handler.setLevel(logging.DEBUG)
    else:
        stream_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s: %(name)s - %(funcName)s - %(levelname)s: %(message)s')

    # Add formatters to our handlers
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add Handlers to our logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # Return the logger for future use
    return logger 

def signal_handler(sig, frame):    
    print('\nCtrl-C entered. Killing processes.')
    os.killpg(0, signal.SIGKILL)
    sys.exit(0)

def configure_tinyrad():
    # TODO: Clean-up, add more functionality?

    # Setup Connection
    Brd = TinyRad.TinyRad('Usb')
    
    # Reset Board
    reset_status = Brd.BrdRst()

    # Software Version
    sw_version = Brd.BrdDispSwVers()

    # Configure Receiver
    Brd.RfRxEna()

    # Configure Transmitter 
    tx_power = 100
    Brd.RfTxEna(1, tx_power)
    Brd.RfTxEna(2, tx_power)
    
    return Brd

def plot_time_signals(DataV, num_channels, N):
    # TODO: Clean-up -- do I need to keep this?

    N = np.arange(int(N))

    fig, ax = plt.subplots(4, sharex='col', sharey='row', num=99, clear=True)

    #plt.figure('Time Signals')

    #for chan_index in np.arange(2*num_channels - 1):
    #    plt.plot(N[1:], DataV[:, chan_index], label = str('Channel ' + \
    #                                                  str(chan_index)))

    ax[0].plot(N[1:], DataV[:, 0])
    ax[0].set(xlabel='Sample', ylabel='ADC Counts', title='Channel 1')
    ax[1].plot(N[1:], DataV[:, 1])
    ax[1].set(xlabel='Sample', ylabel='ADC Counts', title='Channel 2')
    ax[2].plot(N[1:], DataV[:, 2])
    ax[2].set(xlabel='Sample', ylabel='ADC Counts', title='Channel 3')
    ax[3].plot(N[1:], DataV[:, 3])
    ax[3].set(xlabel='Sample', ylabel='ADC Counts', title='Channel 4')

    plt.draw()
    #plt.legend()
    plt.pause(0.0001)
    plt.clf()

def plot_range_profile(rp_iq_data, sigpro_cfg):
    plt.figure('Amplitude vs Range Across 7-element Virtual Array of Channels')

    amplitudes = []
    for chan_index in np.arange(2*sigpro_cfg.num_channels - 1):
        chan_amp_db = 20*np.log10(np.abs(rp_iq_data[:, chan_index]))
        chan_phase = np.angle(rp_iq_data[:, chan_index])
        amplitudes.append(chan_amp_db)
        plt.plot(sigpro_cfg.range_extent_vec, chan_amp_db, \
                 label = str('Channel ' + str(chan_index)))

    plt.draw()
    plt.legend()
    plt.xlim([min(sigpro_cfg.range_extent_vec), \
              max(sigpro_cfg.range_extent_vec)])
    plt.pause(0.0001)
    plt.clf()

    return

def plot_heat_map(normalized_amp, sigpro_cfg):

    if sigpro_cfg.tactical_mode is True:
        #plt.imshow(normalized_amp, cmap='hot', interpolation='none', \
        plt.imshow(normalized_amp, interpolation='none', \
                   extent=[sigpro_cfg.range_extent_vec[0],\
                           sigpro_cfg.range_extent_vec[-1],\
                           sigpro_cfg.filt_angle_vec[0],
                           sigpro_cfg.filt_angle_vec[-1]], \
                   aspect='auto')
    else:
        #plt.imshow(normalized_amp, cmap='hot', interpolation='none', \
        plt.imshow(normalized_amp, interpolation='none', \
                   extent=[sigpro_cfg.range_extent_vec[0],\
                           sigpro_cfg.range_extent_vec[-1],\
                           sigpro_cfg.angle_extent_vec[0],
                           sigpro_cfg.angle_extent_vec[-1]], \
                   aspect='auto')

    plt.draw()
    plt.pause(0.0001)
    plt.clf()

    return

def plot_az_data(normalized_amp, sigpro_cfg):
    plt.figure('Amplitude vs Range for All Azimuth Angles')

    for range_sample in normalized_amp.T:
        plt.plot(sigpro_cfg.angle_extent_vec, range_sample)
    plt.xlim([min(sigpro_cfg.angle_extent_vec), max(sigpro_cfg.angle_extent_vec)])
    plt.draw()
    plt.pause(0.0001)
    plt.clf
        
    return

def plot_sum_data(rp_iq_data, sigpro_cfg):

    for az_increment in compute_sum_data(rp_iq_data, sigpro_cfg):
        plt.plot(sigpro_cfg.range_extent_vec, az_increment)
    plt.xlim([min(sigpro_cfg.range_extent_vec), max(sigpro_cfg.range_extent_vec)])
    plt.draw()
    plt.pause(0.0001)
    plt.clf()

    return

# TODO: Either delete this or figure out what is useful from it
    #amplitudes = []
    #angles = []

    #for chan_index in np.arange(2*num_channels - 1):
    #    chan_amp_iq = np.abs(rp_iq_data[:, chan_index]) 
    #    chan_phase = np.angle(rp_iq_data[:, chan_index])
    #    amplitudes.append(chan_amp_iq)
    #    angles.append(chan_phase)


    #for chan_index in np.arange(2*num_channels - 1):
    #    iq_sum += amplitudes[chan_index]*np.exp(-1j*angles[chan_index])


    ## RM DEBUG END

    ##noise_floor = -106.809205223974
    ##sum_amp = 20*np.log10(np.abs(iq_sum))-noise_floor
    #sum_amp = 20*np.log10(np.abs(iq_sum))
    ##sum_angle = np.angle(iq_sum)

    #plt.plot(range_extent_vec, sum_amp)
    ##plt.plot(range_extent_vec, sum_angle)
    #plt.xlim([min(range_extent_vec), max(range_extent_vec)])
    ##plt.ylim(-20, 50)
    #plt.draw()
    #plt.pause(0.0001)
    #plt.clf()

    ##print(np.average(sum_amp))

    #return iq_sum, sum_amp

def compute_sum_data(rp_iq_data, sigpro_cfg):
    # Create 2D "Heat Map" of I/Q data
    amplitude_map_iq = (np.fft.fftshift(
                        np.fft.fft(rp_iq_data * sigpro_cfg.ant_window_2d, \
                                                sigpro_cfg.NFFTAnt, axis=1)/ \
                                                sigpro_cfg.sca_ant_window, axes=1))

    # Convert to dB
    amplitude_map_db = 20*np.log10(np.abs(amplitude_map_iq)).T

    # If tactical mode, filter out data outside +/- 22.5 degrees before normalizing
    if sigpro_cfg.tactical_mode is True:
        amplitude_map_db = filter_azimuth(amplitude_map_db, sigpro_cfg)

    # Pull out the max and normalize the 2D matrix
    amp_max  = np.max(amplitude_map_db)
    normalized_amp = amplitude_map_db - amp_max # subtract instead of divide since it's log math

    # Filter out values with amplitudes below threshold "floor" value
    amp_floor = sigpro_cfg.noise_floor # More negative == more sensitive
    normalized_amp[normalized_amp < amp_floor] = amp_floor 

    return normalized_amp # Normalized Amplitude, indexed by Angle and then Sample

def filter_azimuth(amplitude_array, sigpro_cfg):
    # Find indices for where angle_extent_vec is equal to +/- 22.5 deg
    min_idx = np.absolute(sigpro_cfg.angle_extent_vec + 22.5).argmin()
    max_idx = np.absolute(sigpro_cfg.angle_extent_vec - 22.5).argmin()

    # Filter the amplitude array using these values
    filtered_array = amplitude_array[min_idx:max_idx,:]

    return filtered_array

def no_detection_check(normalized_amp, sigpro_cfg):
    average_db = np.average(normalized_amp)

    # return True to indicate "no detections" if average_db is less negative
    # than the detection threshold, indicating that the average is close to the
    # maximum and likely caused by noise
    if np.abs(average_db) < np.abs(sigpro_cfg.detection_thresh):
        return True
    else:
        return False

def compute_range_and_angle(normalized_amp, sigpro_cfg):
    # Initialize intermediate variables
    max_val_tmp      = -1111
    tgt_range_sample = None
    tgt_angle_sample = None

    # Perform processing to handle situations where there are NO targets,
    # since we don't want to report the range/angle of the max amplitude
    if no_detection_check(normalized_amp, sigpro_cfg) is True:
        return None, None, None

    # Iterate over each angle increment
    for angle_idx, angle_data in enumerate(normalized_amp):
        # If the max amplitude across all range samples for the given angle
        # increment is larger than the stored max, save the new max and store
        # the range sample and angle increment/sample at which the max amplitude
        # was found
        if angle_data.max() > max_val_tmp:
            max_val_tmp = angle_data.max()
            
            tgt_range_sample = angle_data.argmax()
            tgt_angle_sample = angle_idx

    # Index the range and angle extent vectors using the saved max amp indices
    range_val = sigpro_cfg.range_extent_vec[tgt_range_sample]
    if sigpro_cfg.tactical_mode is True:
        angle_val = sigpro_cfg.filt_angle_vec[tgt_angle_sample]
    else:
        angle_val = sigpro_cfg.angle_extent_vec[tgt_angle_sample]

    # DEBUG
    #print(f"Average amplitude = {np.average(normalized_amp):.4f} dB")

    # Return range, angle, and amplitude
    return range_val, angle_val, max_val_tmp

def samples_to_meters(samples, sigpro_cfg):
    # TODO: Figure out where this is useful
    assert isinstance(samples, np.ndarray)
    return sigpro_cfg.range_extent_vec[samples]

def get_detections(normalized_amp, sigpro_cfg):
    # TODO: Work on this or delete
    dets = []

    thresh_db = -10

    for i, az_data in enumerate(normalized_amp):
        filter_arr = az_data > thresh_db
        new_az_data = az_data[filter_arr]
        range_samples = np.argwhere(az_data > thresh_db).T
        if range_samples.any():
            #print(samples_to_meters(range_samples, sigpro_cfg))
            avg_range = np.average(samples_to_meters(range_samples, sigpro_cfg))
            #print(f"Az: {sigpro_cfg.angle_extent_vec[i]:.4f} deg, Range: {avg_range:.4f} m") 

    return True

def check_engagement_zone(range_m, angle_deg, sigpro_cfg):
    if range_m > (sigpro_cfg.min_range + feet_to_m(5)) and \
       range_m < (sigpro_cfg.max_range - feet_to_m(5)) and \
       angle_deg > -12.5 and angle_deg < 12.5:
        return True

    return False

def feet_to_m(feet):
    return feet*0.3048

def radar_search(Brd, sigpro_cfg, plot_cfg):
    # Store SigPro Config object variables locally
    num_samples         = sigpro_cfg.num_samples
    num_channels        = sigpro_cfg.num_channels
    hann_window_2d      = sigpro_cfg.hann_window_2d
    sca_hann_window     = sigpro_cfg.sca_hann_window
    min_range_idx       = sigpro_cfg.min_range_idx
    max_range_idx       = sigpro_cfg.max_range_idx
    NFFT                = sigpro_cfg.NFFT
    range_extent_vector = sigpro_cfg.range_extent_vec
    logger              = sigpro_cfg.logger

    #--------------------------------------------------------------------------
    # Radiate and Perform Signal Processing
    #--------------------------------------------------------------------------
    while True:
        # Record data for Tx1 and Tx2
        Data = Brd.BrdGetData() # NOTE: RF SAFETY IMPLICATIONS

        if plot_cfg.frame_numbers is True:
            # Framenumber is used to check measurement sequence.
            # Odd Framenumbers are for TX1 and even frame numbers for TX2
            # If a frame is missing: DBF processing will fail!!
            frame_counter = Data[0,:]
            logger.debug(f"FrmCntr: {frame_counter}")

        # Format data for virtual array and remove overlapping element
        DataV = np.concatenate((Data[1:num_samples,:], \
                                Data[num_samples+1:,1:]), axis=1)

        # Calculate range profile including calibration
        rp_iq_data = 2 * np.fft.fft(DataV[:,:] * hann_window_2d, n=NFFT, axis=0) \
                        / sca_hann_window * Brd.FuSca

        # Filter out IQ data outside min to max range
        rp_iq_data = rp_iq_data[min_range_idx:max_range_idx,:]

        # Get normalized amplitude matrix, indexed by angle increment and then range sample 
        normalized_amp = compute_sum_data(rp_iq_data, sigpro_cfg) 

        #detection_list = get_detections(normalized_amp, sigpro_cfg)
        
        # Pull out range and angle values of maximum amplitude detection after
        # filtering out azimuth data outside 22.5 degrees and checking the max 
        # amplitude against a detection threshold across all range/azimuth 
        # points, since we do not want the radar to report a detection if the
        # max is just noise.
        #
        #   range_val units: meters
        #   angle_val units: degrees
        #   amplitude units: dB (relative)
        range_val, angle_val, amplitude = compute_range_and_angle(normalized_amp, sigpro_cfg)

        if range_val is not None:
            engagement_zone_flag = check_engagement_zone(range_val, angle_val, sigpro_cfg)

            # TODO: ADD IN COORDINATE TRANSFORMATION BASED ON ZONE

            #logger.info(f"Range: {range_val:.4f} m, Azimuth: {angle_val:.4f} deg, Amplitude: {amplitude:.4f} dB")
            logger.info(f"Range: {range_val:.4f} m, Azimuth: {angle_val:.4f} deg, Engagement Zone: {engagement_zone_flag}")

            # Send radar_report via DDS
            if sigpro_cfg.dds_enabled is True:
                sigpro_cfg.radar_report_writer.send(range_val, angle_val, sigpro_cfg.zone_number, engagement_zone_flag)
        else:
            logger.debug(f"No detections found. Average Amplitude: {np.average(normalized_amp):.4f}")


        # Plots
        if plot_cfg.time_signals is True:
            plot_time_signals(DataV, num_channels, N)

        if plot_cfg.range_profile is True:
            plot_range_profile(rp_iq_data, sigpro_cfg)

        if plot_cfg.sum_data is True:
            plot_sum_data(rp_iq_data, sigpro_cfg)

        if plot_cfg.az_data is True:
            plot_az_data(normalized_amp, sigpro_cfg)

        if plot_cfg.heat_map is True:
            plot_heat_map(normalized_amp, sigpro_cfg)


if __name__ == "__main__":
    # Initialize Ctrl+C signal handler
    signal.signal(signal.SIGINT, signal_handler)
    os.setpgrp()

    # Initialize argparse and save CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('min_range', type=int, help="Minimum range (in meters) for RF Signal Processing")
    parser.add_argument('max_range', type=int, help="Maximum range (in meters) for RF Signal Processing")
    parser.add_argument('-a', '--az', required=False, help="Flip the sum data plot option to show azimuth versus amplitude", action="store_true")
    parser.add_argument('-l', '--log', required=False, help="Enable debug logging to the command line", action="store_true")
    parser.add_argument('-f', '--floor', required=False, help="Configurable noise floor / threshold", type=int)
    parser.add_argument('-p', '--plot', choices=['frame_nums', 'time_signals', 'range_profile', 'sum_data', 'az_data', 'heat_map'], \
                        required=False, help="Plotting options.")
    parser.add_argument('-d', '--dds', required=False, help="Enable DDS messages to be sent for radar detection reports", action="store_true")
    args = parser.parse_args()

    # Initialize logger
    logger = init_rad_control_logger(args.log)

    # Initialize Plot Config
    plot_cfg = PlotConfig()
    # Modify plot config NOTE: __main__ only, TODO: make this configurable via DDS?
    if args.plot == 'range_profile':    plot_cfg.range_profile  = True
    if args.plot == 'time_signals':     plot_cfg.time_signals   = True
    if args.plot == 'az_data':          plot_cfg.az_data        = True
    if args.plot == 'sum_data':         plot_cfg.sum_data       = True
    if args.plot == 'heat_map':         plot_cfg.heat_map       = True

    if args.floor is None: args.floor = -35

    # Initialize Board object
    Brd = configure_tinyrad()

    # Initialize SigPro Config
    # NOTE: __main__ only -- Adjust min/max range based on CLI arguments
    sigpro_cfg = SigProConfig(Brd, args.min_range, args.max_range, args.floor, args.dds)
    sigpro_cfg.logger = logger
    sigpro_cfg.tactical_mode = True

    # Main loop
    radar_search(Brd, sigpro_cfg, plot_cfg)

    signal.pause()
