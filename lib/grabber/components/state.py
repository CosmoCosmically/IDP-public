####################################################################################################
#
# Holds the states for various grabber components.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################


class ServoState:
    """Servo state enumeration."""
    REST = "REST"  # Initial state
    TURNING = "TURNING"
    IN_POSITION = "IN_POSITION"


class LifterState:
    """Lifter state enumeration."""
    UP = "UP"
    MID = "MID"
    DOWN = "DOWN"


class JawState:
    """Jaw state enumeration."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PickUpState:
    """Pickup state machine enumeration."""
    NONE = "NONE"
    CLOSING_JAW = "CLOSING_JAW"
    RAISING_LIFTER = "RAISING_LIFTER"


class DropOffState:
    """Dropoff state machine enumeration."""
    NONE = "NONE"
    OPENING_JAW = "OPENING_JAW"


class GrabberState:
    """High-level grabber state enumeration."""
    REST = "REST"
    PICKING_UP = "PICKING_UP"
    PICKED_UP = "PICKED_UP"
    DROPPING_OFF = "DROPPING_OFF"
    DROPPED_OFF = "DROPPED_OFF"


class ResistanceSenseState:
    """Resistance sensing state enumeration."""
    REST = "REST"  # Default state
    OPEN = "OPEN"  # No reel detected
    DETECTED = "DETECTED"


class PickupState:
    """Pickup status enumeration."""
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
