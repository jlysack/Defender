#!/usr/bin/python3

import sys, os
sys.path.append("../")
import Class.TinyRad as TinyRad
import time as time
import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import signal
import constants as const

def signal_handler(sig, frame):    
    print('\nCtrl-C entered. Killing processes.')
    sys.exit(0)

def configure_tinyrad():
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

def plot_time_signals(DataV, NrChn, N):
    N = np.arange(int(N))

    plt.figure('Time Signals')

    for chan_index in np.arange(2*NrChn - 1):
        plt.plot(N[1:], DataV[:, chan_index], label = str('Channel ' + \
                                                      str(chan_index)))
    plt.draw()
    plt.legend()
    plt.pause(0.0001)
    plt.clf()

def plot_range_profile(rp_iq_data, range_extent_vec, NrChn, N):
    plt.figure('Range Profile')

    amplitudes = []
    for chan_index in np.arange(2*NrChn - 1): # TODO: figure out why it's 2*num_chan - 1
        chan_amp_db = 20*np.log10(np.abs(rp_iq_data[:, chan_index]))
        amplitudes.append(chan_amp_db)
        plt.plot(range_extent_vec, chan_amp_db, label = str('Channel ' + \
                                                         str(chan_index)))
    plt.draw()
    plt.legend()
    plt.xlim([min(range_extent_vec), max(range_extent_vec)])
    plt.ylim([-100, -35])
    plt.pause(0.0001)
    plt.clf()

    return amplitudes

def plot_sum_data(rp_iq_data, range_extent_vec, NrChn, N):
    plt.figure('Sum Data')

    iq_sum = np.zeros_like(rp_iq_data[:, 0])

    for chan_index in np.arange(2*NrChn - 1):
        iq_sum += rp_iq_data[:, chan_index]

    sum_amp = 20*np.log10(np.abs(iq_sum))

    plt.plot(range_extent_vec, sum_amp)
    plt.xlim([min(range_extent_vec), max(range_extent_vec)])
    plt.draw()
    plt.pause(0.0001)
    plt.clf()

    return iq_sum, sum_amp

def main_loop(Brd, sigpro_cfg, display_cfg):
    # TODO: Replace sigpro_cfg with a class/object SigProConfig
    N = sigpro_cfg['num_samples']
    NrChn = sigpro_cfg['num_channels']
    Win2D = sigpro_cfg['Win2D']
    ScaWin = sigpro_cfg['ScaWin']
    RMin = sigpro_cfg['min_range']
    RMax = sigpro_cfg['max_range']
    RMinIdx = sigpro_cfg['min_range_idx']
    RMaxIdx = sigpro_cfg['max_range_idx']
    NFFT = sigpro_cfg['NFFT']
    vRangeExt = sigpro_cfg['range_extent_vec']

    #--------------------------------------------------------------------------
    # Measure and calculate DBF
    #--------------------------------------------------------------------------
    while True:
        # Record data for Tx1 and Tx2
        Data = Brd.BrdGetData()

        #if Disp_FrmNr > 0:
        #    # Framenumber is used to check measurement sequence.
        #    # Odd Framenumbers are for TX1 and even frame numbers for TX2
        #    # If a frame is missing: DBF processing will fail!!
        #    FrmCntr     =   Data[0,:]
        #    #print("FrmCntr: ", FrmCntr)

        # Format data for virtual array and remove overlapping element
        DataV = np.concatenate((Data[1:N,:], Data[N+1:,1:]), axis=1)

        # Calculate range profile including calibration
        RP = 2*np.fft.fft(DataV[:,:]*Win2D, n=NFFT, axis=0)/ScaWin*Brd.FuSca
        RP = RP[RMinIdx:RMaxIdx,:] # IQ data for ranges between RMin and RMax


        if display_cfg['time_signals'] is True:
            plot_time_signals(DataV, NrChn, N)

        if display_cfg['range_profile'] is True:
            chan_amps_db                = plot_range_profile(RP, vRangeExt, NrChn, N)

        if display_cfg['sum_data'] is True:
            sum_chan_iq, sum_chan_db    = plot_sum_data(RP, vRangeExt, NrChn, N)

        #if Disp_JOpt > 0:
        #    JOpt = np.fft.fftshift(np.fft.fft(RP*WinAnt2D, NFFTAnt, axis=1)/ScaWinAnt, axes=1)

        #    JdB = 20*np.log10(np.abs(JOpt))
        #    JMax = np.max(JdB)
        #    JNorm = JdB - JMax
        #    JNorm[JNorm < -25] = -25

        #    Img.setImage(JNorm.T, pos=[-1,RMin], scale=[2.0/NFFTAnt,(RMax - RMin)/vRangeExt.shape[0]])
        #    View.setAspectLocked(False)

def configure_sigpro(Brd):
    # TODO: Change brd_cfg dict to class/object BrdCfg (maybe have them both inherit from a general Config class)
    sigpro_cfg = dict()
    # Configure Measurements
    # Cfg.Perd: time between measuremnets: must be greater than 1 us*N + 10us
    # Cfg.N: number of samples collected: 1e66 * TRampUp = N; if N is smaller
    # only the first part of the ramp is sampled; if N is larger than the
    brd_cfg = dict()
    brd_cfg['fStrt']        = 24.00e9
    brd_cfg['fStop']        = 24.25e9
    brd_cfg['TRampUp']      = 256e-6
    brd_cfg['Perd']         = 0.4e-3  # 400 us
    brd_cfg['N']            = 256
    brd_cfg['Seq']          = [1, 2]
    brd_cfg['CycSiz']       = 4
    brd_cfg['FrmSiz']       = 128
    brd_cfg['FrmMeasSiz']   = 1 

    Brd.RfMeas(brd_cfg)


    # Read actual board configuration
    NrChn    = int(Brd.Get('NrChn'))
    N        = int(Brd.Get('N'))
    fs       = Brd.Get('fs')        # Sampling Frequency (1 MHz)

    # Configure Signal Processing
    
    # Processing of Range Profile
    NFFT = 2**12

    Win2D = Brd.hanning(N-1, 2*NrChn-1)
    ScaWin = np.sum(Win2D[:,0])
    kf = Brd.Get('kf')
    vRange = np.arange(NFFT)/NFFT*fs*c0/(2*kf)

    # Configure range interval to be displayed
    RMin = 0 # meters
    RMax = 5 # meters
    RMinIdx = np.argmin(np.abs(vRange - RMin)) # array index of RMin meters
    RMaxIdx = np.argmin(np.abs(vRange - RMax)) # array index of RMax meters
    vRangeExt = vRange[RMinIdx:RMaxIdx]        # array of ranges between RMin and RMax

    # Window function for receive channels
    NFFTAnt = 256
    WinAnt2D = Brd.hanning(2*NrChn-1, len(vRangeExt))
    ScaWinAnt = np.sum(WinAnt2D[:,0])
    WinAnt2D = WinAnt2D.transpose()
    vAngDeg  = np.arcsin(2*np.arange(-NFFTAnt//2, NFFTAnt//2)/NFFTAnt)/np.pi*180

    sigpro_cfg['board_params']      = brd_cfg
    sigpro_cfg['num_channels']      = NrChn
    sigpro_cfg['num_samples']       = N
    sigpro_cfg['samp_freq']         = fs
    sigpro_cfg['NFFT']              = NFFT
    sigpro_cfg['Win2D']             = Win2D
    sigpro_cfg['ScaWin']            = ScaWin
    sigpro_cfg['kf']                = kf
    sigpro_cfg['vRange']            = vRange
    sigpro_cfg['min_range']         = RMin
    sigpro_cfg['max_range']         = RMax
    sigpro_cfg['min_range_idx']     = RMinIdx
    sigpro_cfg['max_range_idx']     = RMaxIdx
    sigpro_cfg['range_extent_vec']  = vRangeExt
    sigpro_cfg['NFFTAnt']           = NFFTAnt
    sigpro_cfg['WinAnt2D']          = WinAnt2D
    sigpro_cfg['ScaWinAnt']         = ScaWinAnt
    sigpro_cfg['vAngDeg']           = vAngDeg

    return sigpro_cfg

if __name__ == "__main__":
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Configure plots
    # TODO: Change Display Config dict to a class/object
    display_cfg = dict()
    display_cfg['frame_numbers']     = False # display frame numbers
    display_cfg['time_signals']      = True # display time signals
    display_cfg['range_profile']     = False  # display range profiles
    display_cfg['sum_data']          = False # display sum of all (7) range profile channels
    display_cfg['dbf_cost_function'] = False # display "cost function for dbf"

    # Constants
    c0 = const.c0

    Brd = configure_tinyrad()

    sigpro_cfg = configure_sigpro(Brd)


    main_loop(Brd, sigpro_cfg, display_cfg)

    del Brd

    signal.pause()

    # TODO: Implement section for configuration of hardware
    # TODO: Implement section for configuration of signal processor constants
        # TODO: Make both of the above configurable on-the-fly
    # TODO: Implement board control function (reset, get data, etc.) with return
            # value checking
    # TODO: Implement signal processor functions (built-in) and add comments
    # TODO: Implement detection list functionality (1 target, or multiple targets?)
