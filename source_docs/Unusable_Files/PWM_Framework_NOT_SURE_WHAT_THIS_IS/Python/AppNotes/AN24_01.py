# Getting Started

# (1) Connect to DemoRad
# (2) Display DSP Software version
# (3) Display UID

import Class.TinyRad as TinyRad

#----------------------------------------
# Setup Connection
#----------------------------------------

Brd = TinyRad.TinyRad()

#----------------------------------------
# Software Version
#----------------------------------------

Brd.BrdDispSwVers()

#----------------------------------------
# Board UID
#----------------------------------------

Uid = Brd.BrdDispUID()

Inf = Brd.BrdDispInf();


