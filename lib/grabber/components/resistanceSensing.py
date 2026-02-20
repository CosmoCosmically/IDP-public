####################################################################################################
#
# Logic related to the servo control.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

from grabber.components.types.resistance import Reel
from machine import ADC  # type: ignore
from utime import sleep_ms  # type: ignore

# Local imports
from logger.logger import logger
from config import RESISTANCE_SENSE_PIN
from grabber.config import (
    RESISTANCE_READING_COUNT,
    OPEN_CIRCUIT_VAL,
    RESISTANCE_OC_FALLBACK_COUNT,
)
from grabber.components.utils.resistance import calculate_reel
from grabber.components.state import ResistanceSenseState as State


class resistanceSensing:
    def __init__(self):
        """Class for resistance sensing."""
        self._raw_resistance = ADC(RESISTANCE_SENSE_PIN)

        self._state = State.REST
        self._reel = None
        self._readings = []
        self._oc_count = 0

    @property
    def reel(self):
        return self._reel

    def start_sense(self):
        logger.log("Resistance sensing - starting sense!")
        self.state = State.OPEN

    def reset(self):
        logger.log("Resistance sensing - resetting sense!")
        self.state = State.REST
        self._readings = []
        self._oc_count = 0

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def _get_reel(self):
        if self._oc_count > RESISTANCE_OC_FALLBACK_COUNT:
            # No good detections, just guess 0
            # TODO: Change to closest node
            logger.log(
                "Resistance sensing - Not getting a good resistance reading - defaulting to reel 0!"
            )
            return Reel.REEL_0
        if len(self._readings) < RESISTANCE_READING_COUNT:
            raw_resistance = self._raw_resistance.read_u16()
            # if raw_resistance > OPEN_CIRCUIT_VAL:
            #     logger.log(
            #         "Resistance sensing - Resistance is greater than O.C threshold, ignoring! {}",
            #         raw_resistance,
            #     )
            #     self._oc_count += 1
            #     # Not a good reading, don't keep
            #     return None
            self._readings.append(raw_resistance)
            return None
        reel = calculate_reel(sum(self._readings) / RESISTANCE_READING_COUNT)
        logger.log("Resistance sensing - got reel {}, vals", reel, self._readings)
        return reel

    def _handler(self):
        if self.state == State.REST:
            # Nothing to do
            return
        elif self.state == State.OPEN:
            self._reel = self._get_reel()
            if self._reel is not None:
                # Detected a reel
                self.state = State.DETECTED
            return
        elif self.state == State.DETECTED:
            # Nothing to do here - reset
            self._readings = []
            return


if __name__ == "__main__":
    r = resistanceSensing()
    while True:
        res = r._raw_resistance.read_u16()
        print("Reel for value {} would be {}", res, calculate_reel(res))
        sleep_ms(100)
