####################################################################################################
#
# Holds the states for various grabber components.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################


class ServoState:
    REST = "REST"  # Initial state
    TURNING = "TURNING"
    IN_POSITION = "IN_POSITION"


class LifterState:
    UP = "UP"
    MID = "MID"
    DOWN = "DOWN"


class JawState:
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PickUpState:
    NONE = "NONE"
    CLOSING_JAW = "CLOSING_JAW"
    RAISING_LIFTER = "RAISING_LIFTER"


class DropOffState:
    NONE = "NONE"
    OPENING_JAW = "OPENING_JAW"


class GrabberState:
    REST = "REST"
    PICKING_UP = "PICKING_UP"
    PICKED_UP = "PICKED_UP"
    DROPPING_OFF = "DROPPING_OFF"
    DROPPED_OFF = "DROPPED_OFF"


class ResistanceSenseState:
    REST = "REST"  # Default state
    OPEN = "OPEN"  # No reel detected
    DETECTED = "DETECTED"


class PickupState:
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
