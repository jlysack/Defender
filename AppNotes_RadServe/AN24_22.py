# Range-Doppler processing for a single channel


# (1) Connect to Radarbook2 and ADF24 Frontend
# (2) Enable Supply
# (3) Configure RX
# (4) Configure TX
# (5) Start Measurements
# (6) Configure signal processing
# (7) Calculate range-Doppler processing for single channel

import sys, os
sys.path.append("../")
import  Class.TinyRad as TinyRad
import  time as time
import  numpy as np
from    numpy import *
from    pyqtgraph.Qt import QtGui, QtCore
import  pyqtgraph as pg

#--------------------------------------------------------------------------
# Configure Script
#--------------------------------------------------------------------------
Disp_RP             =   1;
# Display Video (only possible if camera is enabled in RadServe)
Disp_Video          =   0;  

if Disp_RP > 0:
    App = QtGui.QApplication([])
    viewWin = pg.GraphicsWindow("Plot");          
    viewWin.setBackground((255, 255, 255))
    viewWin.resize(1000,600)
    viewPlot = viewWin.addPlot(title="Range Profile", col=0, row=0)
    viewPlot.showGrid(x=True, y=True)
 
#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd         =   TinyRad.TinyRad('RadServe', '127.0.0.1')

Brd.BrdRst()

#--------------------------------------------------------------------------
# Software Version
#--------------------------------------------------------------------------
Brd.BrdDispSwVers()


Brd.BrdGetCalDat()

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
dCfg['CycSiz'] = 2
dCfg['FrmSiz'] = 200
dCfg['FrmMeasSiz'] = 1

Brd.RfMeas(dCfg)

#--------------------------------------------------------------------------
# Read configured values; 
# In the FPGA the CIC sampling rate reduction filter is configured
# automatically; only an integer R reduction value can be configured;
# Readback the actual sampling frequency
#--------------------------------------------------------------------------
N = int(Brd.Get('N'))
NrChn = int(Brd.Get('NrChn'))
fs = Brd.Get('fs')

#--------------------------------------------------------------------------
# Check TCP/IP data rate:
# 16 Bit * Number of Enabled Channels * Number of Samples are measureed in
# the interval TInt. If the data rate is too high, than frames can be lost
#--------------------------------------------------------------------------
DataRate        =   16*NrChn*N*dCfg['FrmMeasSiz']/(dCfg['FrmSiz']*dCfg['Perd'])
print('DataRate: ', (DataRate/1e6), ' MBit/s')

#--------------------------------------------------------------------------
# Configure FMCW System
#--------------------------------------------------------------------------
Brd.Computation.SetParam('fStrt', dCfg['fStrt'])
Brd.Computation.SetParam('fStop', dCfg['fStop'])
Brd.Computation.SetParam('TRampUp', dCfg['TRampUp'])
Brd.Computation.SetParam('fs', fs)
Brd.Computation.SetParam('FuSca', Brd.FuSca)

#--------------------------------------------------------------------------
# Configure Range Profile
#--------------------------------------------------------------------------
# Set the fft size for the range profiles
Brd.Computation.SetParam('Range_NFFT', 2048)
# Set the minimum and maximum range for returning the range profiles
Brd.Computation.SetParam('Range_RMin', 0)
Brd.Computation.SetParam('Range_RMax', 10)
Brd.Computation.SetParam('Range_SubtractMean', 0)

# Set Calibration data: in this case cal data is ignored and all
# coefficients are set 1o 1.
# Brd.Computation.SetParam('CalRe', ones(1,16));
# Brd.Computation.SetParam('CalIm', ones(1,16));

Brd.Computation.SetType('RangeProfile')

if Disp_RP > 0:
    Pen = [];
    Pen.append(pg.mkPen(color=(  0,  95, 162), width=1))
    Pen.append(pg.mkPen(color=(253, 188,   0), width=1))
    Pen.append(pg.mkPen(color=(253,  68,   0), width=1))
    Pen.append(pg.mkPen(color=(  0,  59, 100), width=1))

    viewCurves = []
    for idxChn in range(0, int(NrChn)):
        viewCurves.append(viewPlot.plot(pen=Pen[idxChn]))

# Read back range bins for the calculated range profile
vRange = Brd.Computation.GetRangeBins()

for Cycles in range(0,10000):
    
    # Returns a 3D array [Range, Chn, Arg1]
    # if arg 1 is set greater 1 then multiple measurements are returned
    # with one call to the function
    RP        =   Brd.BrdGetData(1);
        
    if Disp_RP > 0:
        for idxChn in range(0, int(NrChn)):
            viewCurves[idxChn].setData(vRange[0:], 20*log10(abs(RP[:,idxChn])));
        pg.QtGui.QApplication.processEvents()
    
del Brd

App.quit()