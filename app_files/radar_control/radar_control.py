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
import constants as const
import argparse

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
        stream_handler.setLevel(logging.WARN)

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

def plot_range_profile(rp_iq_data, range_extent_vec, num_channels, N):
    # TODO: Clean-up

    plt.figure('Range Profile')

    amplitudes = []
    for chan_index in np.arange(2*num_channels - 1):
        chan_amp_db = 20*np.log10(np.abs(rp_iq_data[:, chan_index]))
        chan_phase = np.angle(rp_iq_data[:, chan_index])
        amplitudes.append(chan_amp_db)
        plt.plot(range_extent_vec, chan_amp_db, label = str('Channel ' + \
        #plt.plot(range_extent_vec, chan_phase, label = str('Channel ' + \
                                                        str(chan_index)))
    plt.draw()
    plt.legend()
    plt.xlim([min(range_extent_vec), max(range_extent_vec)])
    #plt.ylim([-100, -35])
    plt.pause(0.0001)
    plt.clf()

    return amplitudes

def plot_sum_data(rp_iq_data, range_extent_vec, num_channels, N, sigpro_cfg):
    # TODO: Clean-up this entire section after the return above...
    plt.plot(range_extent_vec, JNorm.T[0])
    plt.xlim([min(range_extent_vec), max(range_extent_vec)])
    plt.draw()
    plt.pause(0.0001)
    plt.clf()

    return JdB, JMax

    amplitudes = []
    angles = []

    for chan_index in np.arange(2*num_channels - 1):
        chan_amp_iq = np.abs(rp_iq_data[:, chan_index]) 
        chan_phase = np.angle(rp_iq_data[:, chan_index])
        amplitudes.append(chan_amp_iq)
        angles.append(chan_phase)


    for chan_index in np.arange(2*num_channels - 1):
        iq_sum += amplitudes[chan_index]*np.exp(-1j*angles[chan_index])


    # RM DEBUG END

    #noise_floor = -106.809205223974
    #sum_amp = 20*np.log10(np.abs(iq_sum))-noise_floor
    sum_amp = 20*np.log10(np.abs(iq_sum))
    #sum_angle = np.angle(iq_sum)

    plt.plot(range_extent_vec, sum_amp)
    #plt.plot(range_extent_vec, sum_angle)
    plt.xlim([min(range_extent_vec), max(range_extent_vec)])
    #plt.ylim(-20, 50)
    plt.draw()
    plt.pause(0.0001)
    plt.clf()

    #print(np.average(sum_amp))

    return iq_sum, sum_amp

def compute_sum_data(rp_iq_data, sigpro_cfg):
    # Create 2D "Heat Map" of I/Q data
    amplitude_map_iq = (np.fft.fftshift(
                        np.fft.fft(rp_iq_data * sigpro_cfg.ant_window_2d, \
                                                sigpro_cfg.NFFTAnt, axis=1)/ \
                                                sigpro_cfg.sca_ant_window, axes=1))

    # Convert to dB
    amplitude_map_db = 20*np.log10(np.abs(amplitude_map_iq))

    # Pull out the max and normalize the 2D matrix
    amp_max  = np.max(amplitude_map_db)
    normalized_amp = amplitude_map_db - amp_max # subtract instead of divide since it's log math

    # Filter out values with amplitudes below threshold "floor" value
    amp_floor = -25 #TODO: Make this value part of sigpro_cfg
    normalized_amp[normalized_amp < amp_floor] = amp_floor 

    return normalized_amp.T # Normalized Amplitude, indexed by Angle and then Sample

def compute_range_and_angle(normalized_amp, sigpro_cfg):
    # Initialize intermediate variables
    max_val_tmp      = -1111
    angle_sample_idx = -1111
    range_sample_idx = -1111

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
    angle_val = sigpro_cfg.angle_extent_vec[tgt_angle_sample]

    return range_val, angle_val

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
        
        # Pull out range and angle values of maximum amplitude detection
        #   range_val units: meters
        #   angle_val units: degrees
        range_val, angle_val = compute_range_and_angle(normalized_amp, sigpro_cfg)

        # Log Range and Angle values
        logger.info(f"Range: {range_val:.4f} m, Azimuth: {angle_val:.4f} deg")

        # TODO: Revisit this section if we decide we want to actually plot things
        if plot_cfg.time_signals is True:
            plot_time_signals(DataV, num_channels, N)

        if plot_cfg.range_profile is True:
            chan_amps_db                = plot_range_profile(rp_iq_data, range_extent_vector, num_channels, N)

        if plot_cfg.sum_data is True:
           sum_chan_iq, sum_chan_db    = plot_sum_data(rp_iq_data, range_extent_vector, num_channels, N, sigpro_cfg)


if __name__ == "__main__":
    # Initialize Ctrl+C signal handler
    signal.signal(signal.SIGINT, signal_handler)
    os.setpgrp()

    # Initialize argparse and save CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('min_range', type=int, help="Minimum range (in meters) for RF Signal Processing")
    parser.add_argument('max_range', type=int, help="Maximum range (in meters) for RF Signal Processing")
    parser.add_argument('-l', '--log', required=False, help="Enable debug logging to the command line", action="store_true")
    args = parser.parse_args()

    # Initialize logger
    logger = init_rad_control_logger(args.log)

    # Initialize Plot Config
    plot_cfg = PlotConfig()

    # Initialize Board object
    Brd = configure_tinyrad()

    # Initialize SigPro Config
    sigpro_cfg = SigProConfig(Brd)
    sigpro_cfg.logger = logger
    
    # NOTE: __main__ only -- Adjust min/max range based on CLI arguments
    sigpro_cfg.min_range = args.min_range
    sigpro_cfg.max_range = args.max_range

    # Main loop
    radar_search(Brd, sigpro_cfg, plot_cfg)

    signal.pause()
