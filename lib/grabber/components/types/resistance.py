####################################################################################################
#
# Types related to resistance sesning.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################


class Reel:
    """
    Enumeration of reel types detected via resistance sensing.
    """
    REEL_0 = 0
    REEL_1 = 1
    REEL_2 = 2
    REEL_3 = 3
    OPEN_CIRCUIT = 4


REEL_ARR = [Reel.REEL_0, Reel.REEL_1, Reel.REEL_2, Reel.REEL_3]
 