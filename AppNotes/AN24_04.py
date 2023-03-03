# AN24_04 -- Accessing Calibration Data

import sys, os
sys.path.append("../")
import Class.TinyRad as TinyRad

# (1) Connect to DemoRad: Check if Brd exists: Problem with USB driver
# (2) Read Calibration Data
# (3) Read Calibration Information

#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd = TinyRad.TinyRad('Usb')

#--------------------------------------------------------------------------
# Software Version
#--------------------------------------------------------------------------
Brd.BrdDispSwVers()

#--------------------------------------------------------------------------
# Read position of antennas
TxPosn = Brd.Get('TxPosn')
RxPosn = Brd.Get('RxPosn')

#--------------------------------------------------------------------------
# Receive the calibration information
#--------------------------------------------------------------------------
CalDat          =   Brd.BrdGetCalDat()

print("CalDat: ", CalDat)

#Brd.BrdSetCalDat(CalDat)

