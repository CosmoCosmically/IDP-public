####################################################################################################
#
# Holds the states for various components.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

"""
Top-level AGV state definitions.

This module defines the high-level operational states for the
autonomous guided vehicle during a full run cycle.
"""

class AGVState:
    """
    High-level finite state machine for the AGV lifecycle.

    States represent macro-level task phases such as navigation,
    pickup, dropoff, and shutdown.
    """
    REST = 0
    MOVING_TO_PICKUP = 1
    PICKING_UP = 2
    MOVING_TO_DROPOFF = 3
    MOVING_TO_DROPOFF_BAY = 4
    DROPPING_OFF = 5
    ENDING_RUN = 6
 