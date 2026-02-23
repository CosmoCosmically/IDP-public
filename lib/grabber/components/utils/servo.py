####################################################################################################
#
# Utility functions related to the servo.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

from grabber.config import SERVO_PULSE_WIDTH


def pulse_width_to_pwm(val: int) -> int:
    """
    Convert a pulse width in microseconds to a PWM duty value.
    """
    return round((val / SERVO_PULSE_WIDTH) * (2**16 - 1))
 