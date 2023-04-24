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
from    pyqtgraph.Qt import QtGui, QtCore
import  pyqtgraph as pg

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
# Read Calibration data; stores calibration data in hdf5 file
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
dCfg['TRampUp'] = 128e-6 
dCfg['Perd'] = 0.2e-3
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

for Elem in dCfg:
    if isinstance(dCfg[Elem],list):
        print(dCfg[Elem])
        Brd.SetFileParam('Cfg_' + str(Elem), np.array(dCfg[Elem], dtype='float64'), 'ARRAY64')
    else:
        Brd.SetFileParam('Cfg_' + str(Elem),dCfg[Elem], 'DOUBLE')

#--------------------------------------------------------------------------
# Check TCP/IP data rate:
# 16 Bit * Number of Enabled Channels * Number of Samples are measureed in
# the interval TInt. If the data rate is too high, than frames can be losed
#--------------------------------------------------------------------------
DataRate        =   16*NrChn*N*dCfg['FrmMeasSiz']/(dCfg['FrmSiz']*dCfg['Perd'])
print('DataRate: ', (DataRate/1e6), ' MBit/s')
NrUsbPkts = 1000
MeasTim = dCfg['FrmSiz']*dCfg['Perd']*NrUsbPkts
print('Measurement Time: ', MeasTim, ' s')
Brd.CreateFile('TestFile', NrUsbPkts)
time.sleep(MeasTim + 2)
Brd.CloseFile();


del Brd