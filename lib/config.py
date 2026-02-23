####################################################################################################
#
# Global config for the AGV code.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

"""
Global configuration constants for the AGV system.

Defines timing parameters, hardware pin mappings, logging configuration,
and shared runtime flags used across navigation, grabber, sensing,
and motion subsystems.
"""

from grabber.components.types.resistance import Reel
from navigation.components.types.lineSensor import LineSensor

# GLOBAL CONSTANTS

# TODO: Do we have to go back to start within 6 min?
RUN_TIME = 360_000
END_FORWARD_TIME = 500

CONTROL_LOOP_POLL_RATE = 200
DEBUG = False
USB_DEBUG = False

# !!! MUST DISABLE IF YOU WANT ROBOT TO RUN MAIN! !!!
DISABLE_RUN = False


class LOG_LEVELS:
    """
    Logging level definitions used by the system logger.
    Lower values correspond to more verbose output.
    """
    TRACE = 0
    DEBUG = 1
    INFO = 2


LOG_LEVEL = DEBUG
LOG_FILE = "robot.log"
MAX_LOG_SIZE = 64 * 1024  # 64 KB


# How many past values to consider in the moving average
MOVING_AVERAGE_HISTORY_SIZE = 5
# Where we decide a line is a line; higher is more conservative
MOVING_AVERAGE_THRESHOLD = 0.5

# PHYSICAL ATTRIBUTES

PWM_FREQ = 1000

# For debug on Mon
DISABLE_LEFT_TOF = False

# Pins:
# 0-7 reserved for motors, 13, 15 for servos

LINE_SENSOR_PINS = {
    LineSensor.OUTER_LEFT: 11,
    LineSensor.INNER_LEFT: 10,
    LineSensor.INNER_RIGHT: 9,
    LineSensor.OUTER_RIGHT: 8,
}

# TODO: Set pins!
LED_PINS = {
    Reel.REEL_1: 18,
    Reel.REEL_2: 19,
    Reel.REEL_0: 20,
    Reel.REEL_3: 21,
}

RESISTANCE_SENSE_PIN = 28

LEFT_I2C_SCL = 17
LEFT_I2C_SDA = 16

RIGHT_I2C_SCL = 27
RIGHT_I2C_SDA = 26

DEFAULT_TOF_ADDR = 0x29
LEFT_TOF_ADDR = 0x30

BUTTON_PIN = 14

# Globals logic

DEBUG = DEBUG or USB_DEBUG
