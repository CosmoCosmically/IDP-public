####################################################################################################
#
# Utils related to the motion control.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# Machine imports

from config import LOG_LEVELS
from navigation.components.types.navigation import JunctionOptions
from navigation.config import JUNCTION_STRAIGHT_GRACE_PERIOD, JUNCTION_TURN_GRACE_PERIOD
from utime import ticks_ms, ticks_diff  # type: ignore

# Local imports

from navigation.state import LineState
from logger.logger import logger


def junction_detection(o_t) -> int | None:  # type: ignore
    """Detect a junction essentially on the leading edge"""
    if o_t:
        logger.log(
            "Junction detection: Detected a junction {}",
            o_t,
            level=LOG_LEVELS.DEBUG,
        )
        junction_start = ticks_ms()
        return junction_start
    else:
        return None


def line_detection(li, ri, i_t, turn_type, turn_start) -> str:
    "Detect the line during a turn"
    grace_period = (
        JUNCTION_STRAIGHT_GRACE_PERIOD
        if turn_type == JunctionOptions.GO_STRAIGHT
        else JUNCTION_TURN_GRACE_PERIOD
    )
    while ticks_diff(ticks_ms(), turn_start) < grace_period:
        return LineState.UNKNOWN

    if turn_type == JunctionOptions.GO_STRAIGHT:
        # If straight we don't (intentionally) come off the line -> no rising edge
        cond = li or ri
    else:
        cond = (li and ri) and not i_t

    if cond:
        logger.log(
            "Line detection: detected new line with inner sensors, transitioning to SUCCESSFUL_JUNCTION",
            level=LOG_LEVELS.DEBUG,
        )
        return LineState.CENTERED
    return LineState.UNKNOWN

    # TODO: Need explicit search pattern if we lose the junction somehow...
