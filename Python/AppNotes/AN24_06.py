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
from    pyqtgraph.Qt import QtGui, QtCore
import  pyqtgraph as pg


# Configure script
Disp_FrmNr = 1;
Disp_TimSig = 1;      # display time signals
Disp_RP = 0;      # display range profile
Disp_RD = 1;      # display range-Doppler map


c0 = 3e8;


if Disp_TimSig > 0 or Disp_RP > 0 or Disp_RD > 0:
    App = QtGui.QApplication([])

if Disp_TimSig > 0:
    

    WinTim = pg.GraphicsWindow(title="Time signals")
    WinTim.setBackground((255, 255, 255))
    WinTim.resize(1000,600)

    PltTim = WinTim.addPlot(title="TimSig", col=0, row=0)
    PltTim.showGrid(x=True, y=True)

if Disp_RP > 0:
    WinRP = pg.GraphicsWindow(title="Range Profile")
    WinRP.setBackground((255, 255, 255))
    WinRP.resize(1000,600)

    PltRP = WinRP.addPlot(title="Range", col=0, row=0)
    PltRP.showGrid(x=True, y=True)

if Disp_RD:
    View = pg.PlotItem(title='Cross Range Plot')
    View.setLabel('left', 'R', units='m')
    View.setLabel('bottom', 'v', units='m/s')

    Img = pg.ImageView(view=View)
    Img.show()
    Img.ui.roiBtn.hide()
    Img.ui.menuBtn.hide()
    #Img.ui.histogram.hide()
    Img.getHistogramWidget().gradient.loadPreset('flame')

#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd = TinyRad.TinyRad()

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
dCfg['Perd'] = 152e-6
dCfg['N'] = 128
dCfg['Seq'] = [1]
dCfg['CycSiz'] = 2
dCfg['FrmSiz'] = 100
dCfg['FrmMeasSiz'] = 32

Brd.RfMeas(dCfg)

#--------------------------------------------------------------------------
# Read actual configuration
#--------------------------------------------------------------------------
N = int(Brd.Get('N'))
NrChn = int(Brd.Get('NrChn'))
fs = Brd.Get('fs')
N = int(Brd.Get('N'))
Np = int(dCfg['FrmMeasSiz'])
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
# Processing of range profile
Win2D = Brd.hanning(N-1,int(Np))
ScaWin = sum(Win2D[:,0])
NFFT = 2**10
NFFTVel = 2**9
kf = (dCfg['fStop'] - dCfg['fStrt'])/dCfg['TRampUp']
vRange = np.arange(NFFT//2)/NFFT*fs*c0/(2*kf)
fc = (dCfg['fStop'] + dCfg['fStrt'])/2

RMin = 1
RMax = 100
RMinIdx = np.argmin(np.abs(vRange - RMin))
RMaxIdx = np.argmin(np.abs(vRange - RMax))
vRangeExt = vRange[RMinIdx:RMaxIdx]

WinVel2D = Brd.hanning(int(Np), len(vRangeExt))
ScaWinVel = sum(WinVel2D[:,0])
WinVel2D = WinVel2D.transpose()

vFreqVel = np.arange(-NFFTVel//2,NFFTVel//2)/NFFTVel*(1/dCfg['Perd'])
vVel = vFreqVel*c0/(2*fc)

#--------------------------------------------------------------------------
# Generate Curves for plots
#--------------------------------------------------------------------------
if Disp_TimSig:
    n = np.arange(int(N))
    CurveTim = []
    for IdxFrm in np.arange(Np):
        CurveTim.append(PltTim.plot(pen=pg.intColor(IdxFrm, hues=Np)))

if Disp_RP:
    CurveRP = []
    for IdxFrm in np.arange(Np):
        CurveRP.append(PltRP.plot(pen=pg.intColor(IdxFrm, hues=Np)))   


#--------------------------------------------------------------------------
# Measure and calculate Range Doppler Map
#--------------------------------------------------------------------------
# Select channel to be processed. ChnSel <= NrChn
ChnSel = 0

for Cycles in range(0, 1000):
    
    Data = Brd.BrdGetData()
    if Disp_FrmNr  > 0:
        FrmCntr     =   Data[0,:]
        print("FrmCntr: ", FrmCntr)

    # Reshape measurement data for range doppler processing
    # 2D array with [N, NLoop]
    MeasChn = np.reshape(Data[:,ChnSel],(N, Np), order='F')

    # Calculate range profiles and display them
    RP = 2*np.fft.fft(MeasChn[1:,:]*Win2D, n=NFFT, axis=0)/ScaWin*Brd.FuSca
    RP = RP[RMinIdx:RMaxIdx,:]
    
      
    if Disp_TimSig > 0:
        # Display time domain signals
        for IdxFrm in np.arange(Np):
            CurveTim[IdxFrm].setData(n[1:],MeasChn[1:,IdxFrm])
    
    if Disp_RP > 0:
        for IdxFrm in np.arange(Np):
            CurveRP[IdxFrm].setData(vRangeExt,20*np.log10(np.abs(RP[:,IdxFrm])))
    
    if Disp_RD > 0:
        # Display range doppler map
        RD = np.fft.fftshift(np.fft.fft(RP*WinVel2D, NFFTVel, axis=1)/ScaWinVel, axes=1)
        RDMap = 20*np.log10(np.abs(RD))
        Img.setImage(RDMap.transpose(), pos=[vVel[0],RMin], scale=[(vVel[-1] - vVel[0])/NFFTVel,(RMax - RMin)/len(vRangeExt)]) 
        
        View.setAspectLocked(False)     
    pg.QtGui.QApplication.processEvents()




del Brd