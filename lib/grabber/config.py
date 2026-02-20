####################################################################################################
#
# Holds the config for various grabber components.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

from grabber.components.types.servo import ServoPositions
from grabber.components.types.resistance import Reel

RESISTANCE_READING_COUNT = 5

# TODO: Set properly!
REEL_RESISTANCE_THRESHOLD = {
    Reel.REEL_0: 25000,  # Green!
    Reel.REEL_1: 51000,  # Yellow!
    Reel.REEL_2: 3600,  # BLUE!
    Reel.REEL_3: 48500,  # RED!
}

RESISTANCE_OC_FALLBACK_COUNT = 5
OPEN_CIRCUIT_VAL = 53000
SERVO_POLL_RATE = 50
SERVO_PULSE_WIDTH = 1_000_000 // 50

# Angle to duty conversion
# TODO: Tune!
POS_TO_PULSE_WIDTH = {
    ServoPositions.JAW_OPEN: 1700,
    ServoPositions.JAW_CLOSED: 1350,
    ServoPositions.LIFTER_DOWN: 1300,
    ServoPositions.LIFTER_MID: 1450,
    ServoPositions.LIFTER_UP: 1550,
    ServoPositions.MID: 1500,
}

SERVO_TURN_TIME = 500
