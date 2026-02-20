####################################################################################################
#
# Utils related to the PD control.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

last_error = 0


def calculate_error(line_sensor_arr: list[int]) -> float:
    global last_error
    "Calculate the weighted error from the line sensor readings"
    LO, LI, RI, RO = line_sensor_arr
    active_sensors = LO + LI + RI + RO
    if active_sensors == 0:
        # Line is lost, panic
        # TODO: This does NOT handle it properly, need proper recovery mode
        pass
    else:
        weighted_error = (LO * -3 + LI * -1 + RI * 1 + RO * 3) / active_sensors
        last_error = weighted_error
    return last_error
