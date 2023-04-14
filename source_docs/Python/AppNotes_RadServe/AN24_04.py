# AN24_04 -- Accessing Calibration Data

import Class.TinyRad as TinyRad

# (1) Connect to DemoRad: Check if Brd exists: Problem with USB driver
# (2) Read Calibration Data
# (3) Read Calibration Information

#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd = TinyRad.TinyRad('RadServe', '127.0.0.1')

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

