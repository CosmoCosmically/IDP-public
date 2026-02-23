####################################################################################################
#
# Logic related to the PD control.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
# Read the docs: https://micropython-simple-pid.readthedocs.io/en/latest/
#
####################################################################################################

# library imports
from navigation.simple_pid.PID import PID

# local imports
from navigation.components.utils.PDControl import calculate_error
from navigation.config import PD, MAX_PD_CORRECTION
from config import DEBUG, LOG_LEVELS
from logger.logger import logger


class PDControl:
    """
    Wrapper around PID controller configured for line-following correction.
    """
    def __init__(self):
        self.pd = PID(PD.KP, PD.KI, PD.KD, setpoint=0, scale="cpu")
        self.pd.output_limits = (-MAX_PD_CORRECTION, MAX_PD_CORRECTION)

    # TODO: When is correction None?
    def calculate_correction(self, line_sensor_readings: list[int]) -> float:
        error = calculate_error(line_sensor_readings)
        correction = self.pd(error)
        # Bit verbose but will improve perf when not logging
        if DEBUG:
            logger.log(
                "line_sensor_readings: {} error: {}, correction: {}",
                line_sensor_readings,
                error,
                correction,
                level=LOG_LEVELS.TRACE,
            )
        return correction or 0

    def reset(self):
        """
        Reset internal PID state, typically after a junction or restart.
        """
        self.pd.set_auto_mode(True, 0)
