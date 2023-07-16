#!/usr/bin/env python3

ZONES = {
    1: {
        "ADA_MIN_RANGE": 55.0,  # feet
        "ADA_MAX_RANGE": 75.0,  # feet
        "ADA_MIN_AZ": -45.0,  # degrees
        "ADA_MAX_AZ": 0.0,  # degrees
        "ADA_MIN_EL": 0.0,  # degrees
        "ADA_MAX_EL": 15.0,  # degrees
        "EZ_MIN_RANGE": 60.0,  # feet
        "EZ_MAX_RANGE": 70.0,  # feet
        "EZ_MIN_AZ": -35.0,  # degrees
        "EZ_MAX_AZ": -10.0,  # degrees
        "EZ_MIN_EL": 0.0,  # degrees
        "EZ_MAX_EL": 15.0,  # degrees
        "BORESIGHT_OFFSET": -22.5,  # degrees
        "ID": 1,  # N/A
    },
    2: {
        "ADA_MIN_RANGE": 115.0,  # feet
        "ADA_MAX_RANGE": 135.0,  # feet
        "ADA_MIN_AZ": 0.0,  # degrees
        "ADA_MAX_AZ": 45.0,  # degrees
        "ADA_MIN_EL": 0.0,  # degrees
        "ADA_MAX_EL": 15.0,  # degrees
        "EZ_MIN_RANGE": 120.0,  # feet
        "EZ_MAX_RANGE": 130.0,  # feet
        "EZ_MIN_AZ": 10.0,  # degrees
        "EZ_MAX_AZ": 35.0,  # degrees
        "EZ_MIN_EL": 0.0,  # degrees
        "EZ_MAX_EL": 15.0,  # degrees
        "BORESIGHT_OFFSET": 22.5,  # degrees
        "ID": 2,  # N/A
    },
    3: {
        "ADA_MIN_RANGE": 195.0,  # feet
        "ADA_MAX_RANGE": 215.0,  # feet
        "ADA_MIN_AZ": -22.5,  # degrees
        "ADA_MAX_AZ": 22.5,  # degrees
        "ADA_MIN_EL": 0.0,  # degrees
        "ADA_MAX_EL": 15.0,  # degrees
        "EZ_MIN_RANGE": 200.0,  # feet
        "EZ_MAX_RANGE": 210.0,  # feet
        "EZ_MIN_AZ": -12.5,  # degrees
        "EZ_MAX_AZ": 12.5,  # degrees
        "EZ_MIN_EL": 0.0,  # degrees
        "EZ_MAX_EL": 15.0,  # degrees
        "BORESIGHT_OFFSET": 0.0,  # degrees
        "ID": 3,  # N/A
    },
}

LOCAL_ZONE_PARAMS = {
    "ADA_MIN_AZ": -22.5,  # degrees
    "ADA_MAX_AZ": 22.5,  # degrees
    "EZ_MIN_AZ": -12.5,  # degrees
    "EZ_MAX_AZ": 12.5,  # degrees
    "MIN_EL": 0.0,  # degrees
    "MAX_EL": 15.0,  # degrees
}

DEFAULT_NOISE_FLOOR = -35  # dB (?)

ENGAGE_ZONE_RANGE_OFFSET = 5.0  # feet
ENGAGE_ZONE_ANGLE_LIMIT = 12.5  # degrees

ZONE_1_ANGLE_OFFSET = -22.5  # 22.5 degrees to the left of center
ZONE_2_ANGLE_OFFSET = 22.5  # 22.5 degrees to the right of center
