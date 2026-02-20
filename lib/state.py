####################################################################################################
#
# Holds the states for various components.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################


class AGVState:
    REST = 0
    MOVING_TO_PICKUP = 1
    PICKING_UP = 2
    MOVING_TO_DROPOFF = 3
    MOVING_TO_DROPOFF_BAY = 4
    DROPPING_OFF = 5
    ENDING_RUN = 6
