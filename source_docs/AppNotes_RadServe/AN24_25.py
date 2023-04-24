#!/opt/bitnami/python/bin/python3

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
Disp_TT = 1
# Display Video (only possible if camera is enabled in RadServe)
Disp_Video = 0

if Disp_TT > 0:
    App = QtGui.QApplication([])
    
    viewWin = QtGui.QMainWindow()
    view = pg.GraphicsLayoutWidget()
    viewWin.setCentralWidget(view)
    viewWin.show()
    viewWin.setWindowTitle('Target Tracker')
    viewPlot = view.addPlot()
    viewPlot.setXRange(-150, 150, padding=0)
    viewPlot.setYRange(0, 200, padding=0)
    viewDet = pg.ScatterPlotItem(size=10, pen=None, pxMode=True)
    viewPlot.addItem(viewDet);

#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd         =   TinyRad.TinyRad('RadServe', '127.0.0.1')

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
Brd.Computation.SetParam('Range_SubtractMean', 1)

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

# Configure Kalman Filter
Brd.Computation.SetParam('Track_SigmaX', 0.1)
Brd.Computation.SetParam('Track_SigmaY', 0.1)
# Update Interval for Tracking algorithm
Brd.Computation.SetParam('Track_dT', dCfg['Perd'])


# Define Size of Cluster to be assigned to existing track
Brd.Computation.SetParam('Track_VarX', 0.04)
Brd.Computation.SetParam('Track_VarY', 0.04)
Brd.Computation.SetParam('Track_VarVel', 0.5)
Brd.Computation.SetParam('TT_NumDetections', 50)

# Output detections with cluster information for Tracks
Brd.Computation.SetParam('TT_OutputCluster', 1);
# changing the remCnt influences how long a track may not receive an update without it being deleted
Brd.Computation.SetParam('TT_RemCnt', 20);

NrTracks = 10
Brd.Computation.SetParam('TT_NumTracks', NrTracks)

if Disp_TT > 0:
    Pen = [];
    Pen.append(pg.mkPen(color=(  0,  95, 162), width=1))
    Pen.append(pg.mkPen(color=(253, 188,   0), width=1))
    Pen.append(pg.mkPen(color=(253,  68,   0), width=1))
    Pen.append(pg.mkPen(color=(  0,  59, 100), width=1))
    Pen.append(pg.mkPen(color=(156, 116,   0), width=1))
    Pen.append(pg.mkPen(color=(156,  42,   0), width=1))
    Pen.append(pg.mkPen(color=( 11, 152, 251), width=1))
    Pen.append(pg.mkPen(color=(  0,   5, 176), width=1))
    
    Pen.append(pg.mkPen(color=(  0,  36,  60), width=1))
    Pen.append(pg.mkPen(color=(151, 112,   0), width=1))
    Pen.append(pg.mkPen(color=(151,  41,   0), width=1))
    Pen.append(pg.mkPen(color=(  0,   0,   0), width=1))
    Pen.append(pg.mkPen(color=(140, 108,  16), width=1))
    Pen.append(pg.mkPen(color=(140,  49,  16), width=1))
    Pen.append(pg.mkPen(color=(  3,  94, 157), width=1))
    Pen.append(pg.mkPen(color=( 18,  22, 158), width=1))
    
    Brush = [];
    Brush.append(pg.mkBrush(  0,  95, 162))
    Brush.append(pg.mkBrush(253, 188,   0))
    Brush.append(pg.mkBrush(253,  68,   0))
    Brush.append(pg.mkBrush(  0,  59, 100))
    Brush.append(pg.mkBrush(156, 116,   0))
    Brush.append(pg.mkBrush(156,  42,   0))
    Brush.append(pg.mkBrush( 11, 152, 251))
    Brush.append(pg.mkBrush(  0,   5, 176))
    
    Brush.append(pg.mkBrush(  0,  36,  60))
    Brush.append(pg.mkBrush(151, 112,   0))
    Brush.append(pg.mkBrush(151,  41,   0))
    Brush.append(pg.mkBrush(  0,   0,   0))
    Brush.append(pg.mkBrush(140, 108,  16))
    Brush.append(pg.mkBrush(140,  49,  16))
    Brush.append(pg.mkBrush(  3,  94, 157))
    Brush.append(pg.mkBrush( 18,  22, 158))
    
    viewTrack = []
    viewHist  = []
    for idxTrack in range(0, int(NrTracks)):
        viewHist.append(viewPlot.plot(pen=Pen[idxTrack]))
        view = pg.ScatterPlotItem(size=10, pen=Pen[idxTrack], pxMode=True)
        viewPlot.addItem(view)
        viewTrack.append(view)

Brd.Computation.SetType('TargetTracker')

#--------------------------------------------------------------------------
# Measure and calculate DBF
#--------------------------------------------------------------------------
for MeasIdx in range(0, 10000):

    Data        =   Brd.BrdGetData()
        
   
#        Data of Tracker contains struct array with the following entries
#         Id
#         X
#         Y
#         Vel
#         VelX
#         VelY
#         Mag
#         VarX
#         VarY
#         HistX
#         HistY

    # also plot untracked detections
    viewDet.clear()
    det = []
    if len(Data['Detections']) > 0:
        for Idx in range(0, len(Data['Detections'])):
            det.append({'pos': (Data['Detections'][Idx]['X'], Data['Detections'][Idx]['Y']), 'data': 1, 'pen': pg.mkPen(255,255,255), 'brush': pg.mkBrush(None), 'size': 7});
    
    viewDet.addPoints(det);
    
    for Idx in range(0, len(viewTrack)):
        viewTrack[Idx].clear()
        viewHist[Idx].clear()
        viewTrack[Idx].addPoints([])
        
    for Idx in range(0, len(Data['Tracks'])):
        viewTrack[Idx].addPoints([{'pos': (Data['Tracks'][Idx]['X'], Data['Tracks'][Idx]['Y']), 'data': 1, 'pen':Pen[Idx], 'brush': Brush[Idx], 'size': 10}]);
        viewHist[Idx].setData(Data['Tracks'][Idx]['HistX'], Data['Tracks'][Idx]['HistY'])
        
    pg.QtGui.QApplication.processEvents()

Brd.CloseDataPort();

del Brd

App.quit()
