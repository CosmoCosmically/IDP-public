####################################################################################################
#
# Primary logic for the ToFs.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

from config import (
    DEFAULT_TOF_ADDR,
    DISABLE_LEFT_TOF,
    LEFT_I2C_SCL,
    LEFT_I2C_SDA,
    RIGHT_I2C_SCL,
    RIGHT_I2C_SDA,
)
import math
from utime import sleep_ms  # type: ignore
import uasyncio  # type: ignore
from misc.config import BAY_THRESHOLD, MAX_TRIGGERS, NUM_TRIGGERS
from logger.logger import logger
from machine import Pin, I2C  # type: ignore
from misc.components.utils.VL53L0X import VL53L0X
from misc.state import ToFState as State

# ==========================
# I2C and TOF sensor setup for VL53L0X
# ==========================


class ToFs:
    def __init__(self):
        self.left_i2c_bus = I2C(id=0, sda=Pin(LEFT_I2C_SDA), scl=Pin(LEFT_I2C_SCL))
        self.right_i2c_bus = I2C(id=1, sda=Pin(RIGHT_I2C_SDA), scl=Pin(RIGHT_I2C_SCL))
        if not DISABLE_LEFT_TOF:
            self.left_tof = VL53L0X(self.left_i2c_bus, address=DEFAULT_TOF_ADDR)
            logger.log("I2C LEFT: {}", self.left_i2c_bus.scan())
        self.right_tof = VL53L0X(self.right_i2c_bus, address=DEFAULT_TOF_ADDR)
        logger.log("I2C RIGHT: {}", self.right_i2c_bus.scan())
        self.tofs = (
            (self.right_tof,) if DISABLE_LEFT_TOF else (self.left_tof, self.right_tof)
        )
        for tof in self.tofs:
            tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
            tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)

        self._readings = []
        self.state = State.REST
        self._triggers = 0
        self._total_triggers = 0
        self.occupied = True

    # ==========================
    # start/stop tof
    # ==========================
    def start_tofs(self):
        print("starting ToF sensors...")
        for tof in self.tofs:
            tof.start()
        while not (
            (DISABLE_LEFT_TOF or self.left_tof._started) and self.right_tof._started
        ):
            logger.log("Waiting for ToF sensors to start...")
            sleep_ms(50)
        logger.log("ToF sensors started!")

    def stop_tofs(self):
        for tof in self.tofs:
            tof.stop()
        print("Stopped ToF sensors.")

    def sel_tof(self, side: str):
        return self.left_tof if side == "left" else self.right_tof

    def start_reading(self):
        self.state = State.ACQUIRING_READINGS

    def reset(self):
        self._triggers = 0
        self._total_triggers = 0
        self.occupied = True
        self._readings = []
        self.state = State.REST

    # ==========================
    # Bay detection
    # ==========================
    def read_distance_once(self, side):
        """
        Read one valid distance sample.
        Returns distance in mm, or None if not ready.
        """
        d = self.sel_tof(side).read()
        if d is not None and d > 8000:
            logger.log("Got an 8000 measurement!")
            return None
        return d

    def get_distances(self, side):
        "Get distances until triggered > NUM_TRIGGERS"
        if self._triggers >= NUM_TRIGGERS or self._total_triggers >= MAX_TRIGGERS:
            # Convert 0 readings to 600 readings
            self._readings = [600 if r == 0 else r for r in self._readings]
            # TODO: Less than num_triggers instead?
            if len(self._readings) == 0:
                self.occupied = False
                self.state = State.COMPLETE
                return
            self.occupied = sum(self._readings) / len(self._readings) < BAY_THRESHOLD
            logger.log(
                "ToF: Bay occupied: {}, readings {}",
                self.occupied,
                self._readings,
            )
            self.state = State.COMPLETE
            return
        res = self.read_distance_once(side)
        if res is not None:
            logger.log("ToF: Got a reading {}", res)
            self._readings.append(res)
            self._triggers += 1
        self._total_triggers += 1

    def handler(self, side):
        if self.state == State.ACQUIRING_READINGS:
            self.get_distances(side)


# Instatiate object
tofs = ToFs()


# ==========================
# test usage
# ==========================
async def main():
    print("start test")
    tofs = ToFs()
    tofs.start_tofs()
    tofs.start_reading()
    while tofs.state != State.COMPLETE:
        print("Getting readings...")
        tofs.handler("right")
        await uasyncio.sleep_ms(20)
    print("Right Readings {}, occupied: {} {}", tofs._readings, tofs.occupied)
    tofs.reset()
    tofs.start_reading()
    while tofs.state != State.COMPLETE:
        print("Getting readings...")
        tofs.handler("left")
        await uasyncio.sleep_ms(20)
    print("Left Readings {}, occupied: {}", tofs._readings, tofs.occupied)
    tofs.stop_tofs()
    print("end test")


if __name__ == "__main__":
    uasyncio.run(main())
