####################################################################################################
#
# Utility functions related to the motor.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# TODO: dodgy - is it definitely linear? Should test
def normalise_power(power: int) -> int:
    """Maps the motor power from 0-100 to 0-2^16-1

    Args:
        power: int - Power from 0 - 100

    Returns:
        int - Power mapped from 0 - 2^16-1
    """
    if power > 100:
        power = 100
    elif power < 0:
        power = 0
    return int((2**16 - 1) * (power / 100))

