# Getting Started

# (1) Connect to DemoRad
# (2) Display DSP Software version
# (3) Display UID

import sys, os
sys.path.append("../")
import Class.TinyRad as TinyRad

#----------------------------------------
# Setup Connection
#----------------------------------------

Brd = TinyRad.TinyRad('RadServe', '127.0.0.1')

#----------------------------------------
# Software Version
#----------------------------------------

Brd.BrdDispSwVers()

#----------------------------------------
# Board UID
#----------------------------------------

Uid = Brd.BrdDispUID()

Inf = Brd.BrdDispInf();


