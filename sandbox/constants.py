#!/usr/bin/env python3

# TODO: Maybe instead of variables like this, use dictionaries for each Zone?
# Or dicts for each value by its purpose (ADA_MIN_RANGE with a 1, 2, and            <-- LETS GO WITH THIS METHOD
# 3 option like in the BORESIGHT_OFFSETS variable)
#
# If we create classes/"objects" for zones, we could potentially allow
# ourselves to create zone-specific settings, like ignoring detections
# in a zone temporarily, etc.
 
ADA_MIN_RANGE = {           # feet
    1:  55.0,
    2: 115.0,
    3: 195.0,
}
 
ADA_MAX_RANGE = {           # feet
    1:  75.0,
    2: 135.0,
    3: 215.0,
}
 
ADA_MIN_AZ = {              # degrees
    1: -45.0,
    2:   0.0,
    3: -22.5,
}
 
ADA_MAX_AZ = {              # degrees
    1:  0.0,
    2: 45.0,
    3: 22.5,
}
 
ADA_MIN_EL = {              # degrees
    1: 0.0,
    2: 0.0,
    3: 0.0,
}
 
ADA_MAX_EL = {              # degrees
    1: 15.0,
    2: 15.0,
    3: 15.0,
}
 
EZ_MIN_RANGE = {            # feet
    1:  60.0,
    2: 120.0,
    3: 200.0,
}
 
EZ_MAX_RANGE = {            # feet
    1:  70.0,
    2: 130.0,
    3: 210.0,
}
 
EZ_MIN_AZ = {               # degrees
    1: -35.0,
    2:  10.0,
    3: -12.5,
}
 
EZ_MAX_AZ = {               # degrees
    1: -10.0,
    2:  35.0,
    3:  12.5,
}

EZ_MIN_EL = {               #  degrees
    1: 0.0,
    2: 0.0,
    3: 0.0,
}
 
EZ_MAX_EL = {               # degrees
    1: 15.0,
    2: 15.0,
    3: 15.0,
}
 
BORESIGHT_OFFSET    = {     # degrees
    1 : -22.5,
    2 :  22.5,
    3:      0,
}    
 
ZONE_ENUM = {
    1: 1,
    2: 2,
    3: 3,
}    
