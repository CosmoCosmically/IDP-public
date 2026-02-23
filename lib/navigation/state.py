####################################################################################################
#
# Holds the states for various components.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

"""
Navigation subsystem state definitions.

Contains enumerations for line tracking, motion control,
path following, and dropoff handling.
"""

class LineState:
    """
    Line detection status during motion.
    """
    UNKNOWN = "UNKNOWN"
    CENTERED = "CENTERED"


class MotionState:
    """
    Internal motion control state machine states.
    """
    REST = "REST"
    FOLLOWING_LINE = "FOLLOWING_LINE"
    PRE_JUNCTION = "PRE_JUNCTION"
    JUNCTION = "JUNCTION"
    POST_JUNCTION = "POST_JUNCTION"


class NavigationState:
    """
    High-level navigation mode selector.
    """
    FOLLOWING_PATH = "FOLLOWING_PATH"
    DROPOFF = "DROPOFF"


class PathFollowingState:
    """
    Sub-state machine for route traversal.
    """
    REST = "REST"
    NAVIGATING = "NAVIGATING"
    TURNING = "TURNING"
    COMPLETE = "COMPLETE"


class DropoffState:
    """
    Sub-state machine for dropoff area handling.
    """
    REST = "REST"
    NAVIGATING = "FINDING_BAY"
    TURN_PENDING = "TURN_PENDING"
    TURNING = "TURNING"
    DROPPING_OFF = "DROPPING_OFF"
    COMPLETE = "COMPLETE"
