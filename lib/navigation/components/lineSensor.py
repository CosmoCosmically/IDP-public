####################################################################################################
#
# Logic related to the line sensors.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# Machine imports
from machine import Pin  # type: ignore
from utime import sleep_ms  # type: ignore

# Local imports
from navigation.components.types.lineSensor import LineSensor
from config import (
    LINE_SENSOR_PINS,
    MOVING_AVERAGE_HISTORY_SIZE,
    MOVING_AVERAGE_THRESHOLD,
)
from navigation.components.utils.movingAverage import movingAverage


class lineSensor:
    def __init__(self, line_sensor: int):
        self.pin = Pin(LINE_SENSOR_PINS[line_sensor], Pin.IN)

    def read(self):
        # TODO: validate
        """Reads a line sensor.

        Return - int: 1 if a line is detected, 0 if not
        """
        return self.pin.value()


class lineSensorArray:
    def __init__(self):
        outer_left = lineSensor(LineSensor.OUTER_LEFT)
        inner_left = lineSensor(LineSensor.INNER_LEFT)
        inner_right = lineSensor(LineSensor.INNER_RIGHT)
        outer_right = lineSensor(LineSensor.OUTER_RIGHT)

        # Leading edge detection
        self.o_t = False
        self.i_t = False

        self.line_sensor_arr = (outer_left, inner_left, inner_right, outer_right)
        self.average: movingAverage = movingAverage(size=MOVING_AVERAGE_HISTORY_SIZE)

        self.curr = (0, 0, 0, 0)

    def _read(self) -> tuple[int]:
        values = (ls.read() for ls in self.line_sensor_arr)
        return tuple(values)
        # tuple of size 4 of 0 or 1 for each sensor

    def state(self) -> tuple[int, ...]:
        """Returns the line sensor state with a small moving average.

        Also updates the rising edge detection.
        """
        values = self._read()
        self.average.add(values)

        self.curr = self.average.clamp(MOVING_AVERAGE_THRESHOLD)

        return self.curr

    def update_rising_edge(self):
        lo, li, ri, ro = self.curr
        self.o_t = lo or ro
        self.i_t = li and ri

    @property
    def rising_edge(self):
        return (self.o_t, self.i_t)


if __name__ == "__main__":
    # ls = lineSensor(LineSensor.OUTER_LEFT)
    ls_arr = lineSensorArray()
    while True:
        print(ls_arr.state())
        print(ls_arr.rising_edge)
        ls_arr.update_rising_edge()
        sleep_ms(10)
