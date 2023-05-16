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

def configure_plots_qt(app, display_cfg):
    plot_dict = dict()

    WinTim = None
    WinRP = None
    WinSum = None

    if display_cfg['time_signals'] is True:
        WinTim = pg.GraphicsLayoutWidget(show=False, title="Time signals")
        WinTim.setBackground((255, 255, 255)) 
        WinTim.resize(1000,600)

        plot_dict['time_signals'] = WinTim.addPlot(title="TimSig", col=0, row=0)
        plot_dict['time_signals'].showGrid(x=True, y=True)

    if display_cfg['range_profile'] is True:
        WinRP = pg.GraphicsLayoutWidget(show=False, title="Range Profile")
        WinRP.setBackground((255, 255, 255))
        WinRP.resize(1000,600) 

        plot_dict['range_profile'] = WinRP.addPlot(title="Range", col=0, row=0)
        plot_dict['range_profile'].showGrid(x=True, y=True) 

    if display_cfg['sum_data'] is True:
        WinSum = pg.GraphicsLayoutWidget(show=False, title="Sum Channel Data")
        WinSum.setBackground((255, 255, 255)) 
        WinSum.resize(1000,600)

        plot_dict['sum_data'] = WinSum.addPlot(title="Sum Channel", col=0, row=0)
        plot_dict['sum_data'].showGrid(x=True, y=True)

    if display_cfg['dbf_cost_function'] is True:
        View = pg.PlotItem(title='Cross Range Plot')
        View.setLabel('left', 'R', units='m')
        View.setLabel('bottom', 'u')
 
        Img = pg.ImageView(view=View)
        Img.show() 
        Img.ui.roiBtn.hide() 
        Img.ui.menuBtn.hide()
        #Img.ui.histogram.hide()
        Img.getHistogramWidget().gradient.loadPreset('flame')

    # TODO: Create plot list to return to main function
    return plot_dict, WinTim, WinRP, WinSum

def configure_tinyrad(app, display_cfg):
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
    
    # Configure Measurements
    # Cfg.Perd: time between measuremnets: must be greater than 1 us*N + 10us
    # Cfg.N: number of samples collected: 1e66 * TRampUp = N; if N is smaller
    # only the first part of the ramp is sampled; if N is larger than the
    dCfg = dict()
    dCfg['fStrt']        = 24.00e9
    dCfg['fStop']        = 24.25e9
    dCfg['TRampUp']      = 256e-6
    dCfg['Perd']         = 0.4e-3  # 400 us
    dCfg['N']            = 256
    dCfg['Seq']          = [1, 2]
    dCfg['CycSiz']       = 4
    dCfg['FrmSiz']       = 128
    dCfg['FrmMeasSiz']   = 1 

    Brd.RfMeas(dCfg)

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

    return Brd, N, NrChn, fs

def generate_plot_curves(app, display_cfg, plot_dict, N, NrChn):
    # Generate Curves for plots
    curve_dict = dict()
    if display_cfg['time_signals'] is True:
        n = np.arange(int(N))
        curve_dict['time_signals'] = []
        for chan_index in np.arange(2*NrChn-1):
            curve_dict['time_signals'].append(plot_dict['time_signals'].
                              plot(pen=pg.intColor(chan_index, hues=2*NrChn-1)))

    if display_cfg['range_profile']:
        curve_dict['range_profile'] = []
        for chan_index in np.arange(2*NrChn-1):
            curve_dict['range_profile'].append(plot_dict['range_profile'].
                            plot(pen=pg.intColor(chan_index, hues=2*NrChn-1)))

    if display_cfg['sum_data']:
        curve_dict['sum_data'] = []
        for chan_index in np.arange(2*NrChn-1):
            curve_dict['sum_data'].append(plot_dict['sum_data'].
                             plot(pen=pg.intColor(chan_index, hues=2*NrChn-1)))

    return curve_dict


def plot_time_signals(DataV, NrChn, N):
    N = np.arange(int(N))

    plt.figure('Time Signals')

def plot_range_profile(rp_iq_data, range_extent_vec, NrChn, N):
    plt.figure('Range Profile')

    amplitudes = []
    for chan_index in np.arange(2*NrChn - 1):
        chan_amp = 20*np.log10(np.abs(rp_iq_data[:, chan_index]))
        amplitudes.append(chan_amp)
        plt.plot(range_extent_vec, chan_amp, label = str('Channel ' + \
                                                         str(chan_index)))
    plt.draw()
    plt.pause(0.0001)
    plt.clf()

    return amplitudes

def main_loop(app, Brd, N, NrChn, display_cfg):
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
            amplitudes = plot_range_profile(RP, vRangeExt, NrChn, N)

        if display_cfg['sum_data'] is True:
            plot_sum_data(RP, vRangeExt, NrChn, N)

        if Disp_RP> 0:
            for IdxChn in np.arange(2*NrChn-1):
                amplitudes = 20*np.log10(np.abs(RP[:,IdxChn]))
                CurveRP[IdxChn].setData(vRangeExt,amplitudes)

        if Disp_Sum > 0:
            sum_amp = 0
            rp_iq_data = np.zeros_like(RP[:,0])
            for IdxChn in np.arange(2*NrChn-1):
                 rp_iq_data += RP[:,IdxChn]

            print(rp_iq_data)
            sum_amp = 20*np.log10(np.abs(rp_iq_data))

            print(vRangeExt[sum_amp.argmax()])

            CurveSum[IdxChn].setData(vRangeExt,sum_amp)

        #if Disp_JOpt > 0:
        #    JOpt = np.fft.fftshift(np.fft.fft(RP*WinAnt2D, NFFTAnt, axis=1)/ScaWinAnt, axes=1)

        #    JdB = 20*np.log10(np.abs(JOpt))
        #    JMax = np.max(JdB)
        #    JNorm = JdB - JMax
        #    JNorm[JNorm < -25] = -25

        #    Img.setImage(JNorm.T, pos=[-1,RMin], scale=[2.0/NFFTAnt,(RMax - RMin)/vRangeExt.shape[0]])
        #    View.setAspectLocked(False)


if __name__ == "__main__":
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Configure plots
    display_cfg = dict()
    display_cfg['frame_numbers']     = False # display frame numbers
    display_cfg['time_signals']      = False # display time signals
    display_cfg['range_profile']     = True  # display range profiles
    display_cfg['sum_data']          = False # display sum of all (7) range profile channels
    display_cfg['dbf_cost_function'] = False # display "cost function for dbf"

    # Constants
    c0 = const.c0

    app = QtWidgets.QApplication([])

    #plot_dict, WinTim, WinRP, WinSum = configure_plots(app, display_cfg)

    Brd, N, NrChn, fs = configure_tinyrad(app, display_cfg)
    
    #curve_dict = generate_plot_curves(app, display_cfg, plot_dict, N, NrChn)

    main_loop(app, Brd, N, NrChn, display_cfg)

    del Brd

    signal.pause()

    # TODO: Implement section for configuration of hardware
    # TODO: Implement section for configuration of signal processor constants
        # TODO: Make both of the above configurable on-the-fly
    # TODO: Implement board control function (reset, get data, etc.) with return
            # value checking
    # TODO: Implement signal processor functions (built-in) and add comments
    # TODO: Implement detection list functionality (1 target, or multiple targets?)
