# Range-Doppler processing for a single channel


# (1) Connect to Radarbook2 and ADF24 Frontend
# (2) Enable Supply
# (3) Configure RX
# (4) Configure TX
# (5) Start Measurements
# (6) Configure signal processing
# (7) Calculate range-Doppler processing for single channel

import  Class.TinyRad as TinyRad
import  time as time
import  numpy as np
from    numpy import *
from    pyqtgraph.Qt import QtGui, QtCore
import  pyqtgraph as pg

#--------------------------------------------------------------------------
# Configure Script
#--------------------------------------------------------------------------
Disp_DT             =   1;
# Display Video (only possible if camera is enabled in RadServe)
Disp_Video          =   0;  

if Disp_DT > 0:
    App = QtGui.QApplication([])
    
    viewWin = QtGui.QMainWindow()
    view = pg.GraphicsLayoutWidget()
    viewWin.setCentralWidget(view)
    viewWin.show()
    viewWin.setWindowTitle('Detections')
    viewPlot = view.addPlot()
    viewPlot.setXRange(-150, 150, padding=0)
    viewPlot.setYRange(0, 200, padding=0)
    viewImg = pg.ScatterPlotItem(size=10, pen=None, pxMode=True)
    viewPlot.addItem(viewImg)


#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd = TinyRad.TinyRad('RadServe', '127.0.0.1')

Brd.BrdRst()

#--------------------------------------------------------------------------
# Software Version
#--------------------------------------------------------------------------
Brd.BrdDispSwVers()

#--------------------------------------------------------------------------
# Read Calibration data; required for calculation
#--------------------------------------------------------------------------
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
dCfg['TRampUp'] = 512e-6 
dCfg['Perd'] = 0.6e-3
dCfg['N'] = 512
dCfg['Seq'] = [1]
dCfg['CycSiz'] = 2
dCfg['FrmSiz'] = 100
dCfg['FrmMeasSiz'] = 64

Brd.RfMeas(dCfg)

#--------------------------------------------------------------------------
# Read actual configuration
#--------------------------------------------------------------------------
NrChn = Brd.Get('NrChn')
N = Brd.Get('N')
fs = Brd.Get('fs')

#--------------------------------------------------------------------------
# Check TCP/IP data rate:
# 16 Bit * Number of Enabled Channels * Number of Samples are measureed in
# the interval TInt. If the data rate is too high, than frames can be losed
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
Brd.Computation.SetParam('Range_NFFT', pow(2, ceil(log2(dCfg['N'])) + 1))
# Set the minimum and maximum range for returning the range profiles
Brd.Computation.SetParam('Range_RMin', 20)
Brd.Computation.SetParam('Range_RMax', 150)
Brd.Computation.SetParam('Range_SubtractMean', 0)

#--------------------------------------------------------------------------
# Configure Doppler
#--------------------------------------------------------------------------
Brd.Computation.SetParam('Tp', dCfg['Perd'])
Brd.Computation.SetParam('Np', dCfg['FrmMeasSiz'])
# set fft size for the velocity
Brd.Computation.SetParam('Vel_NFFT', pow(2, ceil(log2(dCfg['FrmMeasSiz'])) + 1))

#--------------------------------------------------------------------------
# Configure Angular Domain
#--------------------------------------------------------------------------
Brd.Computation.SetParam('Ang_NFFT', 128)
Brd.Computation.SetParam('Ang_Flip', 1)             # Flip Angle 
Brd.Computation.SetParam('Ang_Interpolate', 1)

#--------------------------------------------------------------------------
# Configure Detector (Local Maxima in Range-Doppler map)
#--------------------------------------------------------------------------
Brd.Computation.SetParam('Thres_Old', 0.95)
Brd.Computation.SetParam('Thres_Mult', 2.8)
# Brd.Computation.SetParam('Thres_Range1', 70)
# Brd.Computation.SetParam('Thres_Mult2', 2)
# Brd.Computation.SetParam('Thres_Range2', 80)

Brd.Computation.SetType('DetectionList')

for Cycles in range(0, 10000):

    Detections        =   Brd.BrdGetData(1)

    viewImg.clear()
    tar = []
    for Idx in range(size(Detections)):
        
        x = Detections[Idx]['Range'] * math.sin(Detections[Idx]['Ang'])
        y = Detections[Idx]['Range'] * math.cos(Detections[Idx]['Ang'])
        if (Detections[Idx]['Vel'] < 0):
            if (Detections[Idx]['Vel'] < -0.5):
                tar.append({'pos': (x,y), 'data': 1, 'brush': pg.mkBrush(255,0,0,255), 'size': 7})
            else:
                tar.append({'pos': (x,y), 'data': 1, 'brush': pg.mkBrush(255,0,0,255), 'size': 7})
        else:
            if (Detections[Idx]['Vel'] > 0.5):
                tar.append({'pos': (x,y), 'data': 1, 'brush': pg.mkBrush(0,0,255,255), 'size': 7})
            else:
                tar.append({'pos': (x,y), 'data': 1, 'brush': pg.mkBrush(0,0,255,255), 'size': 7})
    
    viewImg.addPoints(tar)
    pg.QtGui.QApplication.processEvents()
        
Brd.CloseDataPort();

del Brd

App.quit()