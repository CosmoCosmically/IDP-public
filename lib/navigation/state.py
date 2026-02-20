####################################################################################################
#
# Holds the states for various components.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################


class LineState:
    UNKNOWN = "UNKNOWN"
    CENTERED = "CENTERED"


class MotionState:
    REST = "REST"
    FOLLOWING_LINE = "FOLLOWING_LINE"
    PRE_JUNCTION = "PRE_JUNCTION"
    JUNCTION = "JUNCTION"
    POST_JUNCTION = "POST_JUNCTION"


class NavigationState:
    FOLLOWING_PATH = "FOLLOWING_PATH"
    DROPOFF = "DROPOFF"


class PathFollowingState:
    REST = "REST"
    NAVIGATING = "NAVIGATING"
    TURNING = "TURNING"
    COMPLETE = "COMPLETE"


class DropoffState:
    REST = "REST"
    NAVIGATING = "FINDING_BAY"
    TURN_PENDING = "TURN_PENDING"
    TURNING = "TURNING"
    DROPPING_OFF = "DROPPING_OFF"
    COMPLETE = "COMPLETE"
