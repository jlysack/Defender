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
Disp_RD             =   1;
# Display Video (only possible if camera is enabled in RadServe)
Disp_Video          =   0;  

if Disp_RD > 0:

    App = QtGui.QApplication([]);
    viewPlot = pg.PlotItem();
    viewPlot.setLabel('left', 'R', units='m')
    viewPlot.setLabel('bottom', 'u')
    
    viewImg     =   pg.ImageView(view = viewPlot, name='Adf24Tx2Rx8_AN24_39')
    viewImg.show()
    viewImg.ui.roiBtn.hide()
    viewImg.ui.menuBtn.hide()
    viewImg.ui.histogram.hide()
    viewImg.getHistogramWidget().gradient.loadPreset('bipolar')


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
dCfg['fStrt'] = 23.95e9
dCfg['fStop'] = 24.25e9
dCfg['TRampUp'] = 128e-6 
dCfg['Perd'] = 0.2e-3
dCfg['N'] = 128
dCfg['Seq'] = [1]
dCfg['CycSiz'] = 2
dCfg['FrmSiz'] = 100
dCfg['FrmMeasSiz'] = 32

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
# Read actual configuration
#--------------------------------------------------------------------------
NrChn = Brd.Get('NrChn')
N = Brd.Get('N')
fs = Brd.Get('fs')

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
Brd.Computation.SetParam('Range_RMin', 0.5)
Brd.Computation.SetParam('Range_RMax', 20)
Brd.Computation.SetParam('Range_SubtractMean', 0)

#--------------------------------------------------------------------------
# Configure Doppler
#--------------------------------------------------------------------------
Brd.Computation.SetParam('Tp', dCfg['Perd'])
Brd.Computation.SetParam('Np', dCfg['FrmMeasSiz'])
# set fft size for the velocity
Brd.Computation.SetParam('Vel_NFFT', pow(2, ceil(log2(dCfg['FrmMeasSiz'])) + 1))

# activate the range profile computation on RadServe and prepare the
# computation class for receiving range-Doppler maps
Brd.Computation.SetType('RangeDoppler')

Brd.CfgRadServe('AddVideoToDataPort',0)

# Read back range bins for the calculated range profile
vRange  = Brd.Computation.GetRangeBins()
vVel    = Brd.Computation.GetVelBins()

#--------------------------------------------------------------------------
# Measure and calculate DBF
#--------------------------------------------------------------------------
for MeasIdx in range(0,1000):

    Data        =   Brd.BrdGetData(1)
    
    if Disp_RD > 0:
        RD          =   mean(abs(Data),2);
        
        viewImg.setImage(20*np.log10(RD), pos=[vVel[0], vRange[0]], scale=[(vVel[-1]-vVel[0])/len(vVel), (vRange[-1]-vRange[0])/len(vRange)]);
        viewPlot.setAspectLocked(False);
        
        pg.QtGui.QApplication.processEvents()

Brd.CloseDataPort();

del Brd

App.quit()