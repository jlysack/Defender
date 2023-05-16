#!/usr/bin/python3
# AN24_02 -- FMCW Basics

# (1) Connect to TinyRad
# (2) Enable Supply
# (3) Configure RX
# (4) Configure TX
# (5) Start Measurements
# (6) Configure calculation of range profile

import sys, os
sys.path.append("../")
import  Class.TinyRad as TinyRad
import  time as time
import  numpy as np
from    pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import  pyqtgraph as pg

Disp_FrmNr = 1
Disp_TimSig = 0
Disp_RP = 1

c0 = 3e8

if Disp_TimSig > 0 or Disp_RP > 0:
    App = QtWidgets.QApplication([])

if Disp_TimSig > 0:
    

    WinTim = pg.GraphicsLayoutWidget(show=True, title="Time signals")
    WinTim.setBackground((255, 255, 255))
    WinTim.resize(1000,600)

    PltTim = WinTim.addPlot(title="TimSig", col=0, row=0)
    PltTim.showGrid(x=True, y=True)

if Disp_RP > 0:

    WinRP = pg.GraphicsLayoutWidget(show=True, title="Range Profile")
    WinRP.setBackground((255, 255, 255))
    WinRP.resize(1000,600)

    PltRP = WinRP.addPlot(title="Range", col=0, row=0)
    PltRP.showGrid(x=True, y=True)

#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd = TinyRad.TinyRad('Usb')

Brd.BrdRst()

#--------------------------------------------------------------------------
# Software Version
#--------------------------------------------------------------------------
Brd.BrdDispSwVers()

#--------------------------------------------------------------------------
# Configure Receiver
#--------------------------------------------------------------------------
Brd.RfRxEna()
TxPwr =   100

#--------------------------------------------------------------------------
# Configure Transmitter (Antenna 0 - 2, Pwr 0 - 100)
#--------------------------------------------------------------------------
Brd.RfTxEna(2, TxPwr)

#--------------------------------------------------------------------------
# Configure Measurements
# Cfg.Perd: time between measuremnets: must be greater than 1 us*N + 10us
# Cfg.N: number of samples collected: 1e66 * TRampUp = N; if N is smaller
# only the first part of the ramp is sampled; if N is larger than the 
# 
#--------------------------------------------------------------------------
dCfg = dict()
dCfg['fStrt'] = 24.00e9
dCfg['fStop'] = 24.25e9
dCfg['TRampUp'] = 128e-6 
dCfg['Perd'] = 0.2e-3
dCfg['N'] = 128
dCfg['Seq'] = [1]
dCfg['CycSiz'] = 4
dCfg['FrmSiz'] = 100
dCfg['FrmMeasSiz'] = 1

Brd.RfMeas(dCfg)

#--------------------------------------------------------------------------
# Read actual configuration
#--------------------------------------------------------------------------
N = int(Brd.Get('N'))
NrChn = int(Brd.Get('NrChn'))
fs = Brd.Get('fs')

print(N)
print(NrChn)

#--------------------------------------------------------------------------
# Check TCP/IP data rate:
# 16 Bit * Number of Enabled Channels * Number of Samples are measureed in
# the interval TInt. If the data rate is too high, than frames can be losed
#--------------------------------------------------------------------------
DataRate        =   16*NrChn*N*dCfg['FrmMeasSiz']/(dCfg['FrmSiz']*dCfg['Perd'])
print('DataRate: ', (DataRate/1e6), ' MBit/s')

#--------------------------------------------------------------------------
# Configure Signal processing
#--------------------------------------------------------------------------
NFFT = 2**14

Win = Brd.hanning(N-1,NrChn)
ScaWin = np.sum(Win[:,0])

kf = (dCfg['fStop'] - dCfg['fStrt'])/dCfg['TRampUp']
vRange = np.arange(NFFT//2)/NFFT*fs*c0/(2*kf)

#--------------------------------------------------------------------------
# Generate Curves for plots
#--------------------------------------------------------------------------
if Disp_TimSig:
    n = np.arange(int(N))
    CurveTim = []
    for IdxChn in np.arange(NrChn):
        CurveTim.append(PltTim.plot(pen=pg.intColor(IdxChn, hues=NrChn)))

if Disp_RP:
    CurveRP = []
    for IdxChn in np.arange(NrChn):
        CurveRP.append(PltRP.plot(pen=pg.intColor(IdxChn, hues=NrChn)))    

for Cycles in range(0, 1000):
    
    Data        =   Brd.BrdGetData()     
    
    if Disp_FrmNr > 0:
        FrmCntr     =   Data[0,:]
        print("FrmCntr: ", FrmCntr)

    if Disp_TimSig > 0:
        # Display time domain signals
        for IdxChn in np.arange(NrChn):
            CurveTim[IdxChn].setData(n[1:],Data[1:,IdxChn])

    if Disp_RP > 0:
        # Calculate range profiles and display them
        RP = 2*np.fft.fft(Data[1:,:]*Win, n=NFFT, axis=0)/ScaWin*Brd.FuSca
        RP = RP[:NFFT//2,:]
        for IdxChn in np.arange(NrChn):
            CurveRP[IdxChn].setData(vRange[0:],20*np.log10(np.abs(RP[0:,IdxChn])))

    if Disp_TimSig > 0 or Disp_RP > 0:
        # Generate Event to update plots
        App.processEvents()
        pass




del Brd
