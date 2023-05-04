# Description:
# Configure FMCW Mode with sequential activation of Tx antennas and measure upchirp IF signal
#
# (1) Connect to Radarbook2 with ADF24 Frontend
# (2) Enable Supply
# (3) Configure RX
# (4) Configure TX
# (5) Start Measurements with TX sequence
# (6) Configure signal processing
# (7) Calculate DBF algorithm

import  Class.TinyRad as TinyRad
import  time as time
import  numpy as np
from    pyqtgraph.Qt import QtGui, QtCore
import  pyqtgraph as pg

# Configure script
Disp_FrmNr = 0
Disp_TimSig = 0         # display time signals
Disp_JOpt = 1           # display cost function for DBF

# Configure script
Disp_FrmNr = 1
Disp_TimSig = 0     # display time signals
Disp_RP = 1      # display range profile
Disp_JOpt = 1      # display cost function for DBF

c0 = 1/np.sqrt(8.85e-12*4*np.pi*1e-7)


if Disp_TimSig > 0 or Disp_RP > 0 or Disp_JOpt > 0:
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

if Disp_JOpt:
    View = pg.PlotItem(title='Cross Range Plot')
    View.setLabel('left', 'R', units='m')
    View.setLabel('bottom', 'u')

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
dCfg['TRampUp'] = 256e-6 
dCfg['Perd'] = 0.4e-3
dCfg['N'] = 256
dCfg['Seq'] = [1, 2]
dCfg['CycSiz'] = 4
dCfg['FrmSiz'] = 128
dCfg['FrmMeasSiz'] = 1

Brd.RfMeas(dCfg)

#--------------------------------------------------------------------------
# Read actual configuration
#--------------------------------------------------------------------------
NrChn = int(Brd.Get('NrChn'))
N = int(Brd.Get('N'))
fs = Brd.Get('fs')

#--------------------------------------------------------------------------
# Configure Signal Processing
#--------------------------------------------------------------------------
# Processing of range profile
NFFT = 2**12

Win2D = Brd.hanning(N-1,2*NrChn-1)
ScaWin = np.sum(Win2D[:,0])
kf = Brd.Get('kf')
vRange = np.arange(NFFT)/NFFT*fs*c0/(2*kf)

# Configure range interval to be displayed
RMin = 1
RMax = 10

RMin = 1
RMax = 10
RMinIdx = np.argmin(np.abs(vRange - RMin))
RMaxIdx = np.argmin(np.abs(vRange - RMax))
vRangeExt = vRange[RMinIdx:RMaxIdx]

# Window function for receive channels
NFFTAnt = 256
WinAnt2D = Brd.hanning(2*NrChn-1, len(vRangeExt))
ScaWinAnt = np.sum(WinAnt2D[:,0])
WinAnt2D = WinAnt2D.transpose()
vAngDeg  = np.arcsin(2*np.arange(-NFFTAnt//2, NFFTAnt//2)/NFFTAnt)/np.pi*180

#--------------------------------------------------------------------------
# Generate Curves for plots
#--------------------------------------------------------------------------
if Disp_TimSig:
    n = np.arange(int(N))
    CurveTim = []
    for IdxChn in np.arange(2*NrChn-1):
        CurveTim.append(PltTim.plot(pen=pg.intColor(IdxChn, hues=2*NrChn-1)))

if Disp_RP:
    CurveRP = []
    for IdxChn in np.arange(2*NrChn-1):
        CurveRP.append(PltRP.plot(pen=pg.intColor(IdxChn, hues=2*NrChn-1))) 


#--------------------------------------------------------------------------
# Measure and calculate DBF
#--------------------------------------------------------------------------
for Cycles in range(0, 1000):
    
    # Record data for Tx1 and Tx2
    Data = Brd.BrdGetData() 

    if Disp_FrmNr > 0:
        # Framenumber is used to check measurement sequence.
        # Odd Framenumbers are for TX1 and even frame numbers for TX2
        # If a frame is missing: DBF processing will fail!!
        FrmCntr     =   Data[0,:]
        print("FrmCntr: ", FrmCntr)

    # Format data for virtual array and remove overlapping element
    DataV = np.concatenate((Data[1:N,:], Data[N+1:,1:]), axis=1)
    #DataV = DataA(2:end,AntIdx);
    
    # Calculate range profile including calibration
    RP = 2*np.fft.fft(DataV[:,:]*Win2D, n=NFFT, axis=0)/ScaWin*Brd.FuSca
    RP = RP[RMinIdx:RMaxIdx,:]
    
    if Disp_TimSig > 0:      
        # Display time domain signals
        for IdxChn in np.arange(2*NrChn-1):
            CurveTim[IdxChn].setData(n[1:],DataV[:,IdxChn])

    if Disp_RP> 0:
        for IdxChn in np.arange(2*NrChn-1):
            CurveRP[IdxChn].setData(vRangeExt,20*np.log10(np.abs(RP[:,IdxChn])))

    if Disp_JOpt > 0:
        JOpt = np.fft.fftshift(np.fft.fft(RP*WinAnt2D, NFFTAnt, axis=1)/ScaWinAnt, axes=1)
        
        JdB = 20*np.log10(np.abs(JOpt))
        JMax = np.max(JdB)
        JNorm = JdB - JMax
        JNorm[JNorm < -25] = -25
    
        Img.setImage(JNorm.T, pos=[-1,RMin], scale=[2.0/NFFTAnt,(RMax - RMin)/vRangeExt.shape[0]]) 
        View.setAspectLocked(False)   


    pg.QtGui.QApplication.processEvents()
    



del Brd
