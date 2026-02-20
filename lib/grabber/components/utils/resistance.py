####################################################################################################
#
# Utility functions related to resistance sensing.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# TODO: This wil not work, update the values!!

from grabber.config import REEL_RESISTANCE_THRESHOLD
from grabber.components.types.resistance import Reel


# TODO: Finalise
def calculate_reel(raw_resistance: float) -> int | None:
    """Maps the raw_resistance to a box

    Args:
        raw_resistance: Either GPIO or ADC reading

    Returns:
        Reel
    """
    print(raw_resistance, REEL_RESISTANCE_THRESHOLD[Reel.REEL_1])
    if raw_resistance > REEL_RESISTANCE_THRESHOLD[Reel.REEL_1]:
        reel = Reel.REEL_1
    elif raw_resistance > REEL_RESISTANCE_THRESHOLD[Reel.REEL_3]:
        reel = Reel.REEL_3
    elif raw_resistance > REEL_RESISTANCE_THRESHOLD[Reel.REEL_0]:
        reel = Reel.REEL_0
    else:
        reel = Reel.REEL_2
    return reel
