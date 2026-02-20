####################################################################################################
#
# Logic related to the motor control.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

from machine import Pin, PWM  # type: ignore
from navigation.config import LEFT_MOTOR_BIAS, RIGHT_MOTOR_BIAS, ROBOT_SPEED
from utime import sleep_ms  # type: ignore
from navigation.components.utils.motor import normalise_power
from navigation.components.types.motor import Motor, Direction
from logger.logger import logger

from config import DEBUG, LOG_LEVELS, PWM_FREQ

MOTOR = {
    Motor.LEFT: {"name": "right", "dir": 4, "PWM": 5},
    Motor.RIGHT: {"name": "left", "dir": 7, "PWM": 6},  # why are these reversed...
}


class motorController:
    def __init__(self, motor: int):
        """Initiate a motor controller for a motor

        Args: motor - Motor: motor we want to control
        """
        motor_info = MOTOR[motor]
        self.name, dir_pin, PWM_pin = (
            motor_info["name"],
            motor_info["dir"],
            motor_info["PWM"],
        )
        # set motor direction pin
        self.mDir = Pin(dir_pin, Pin.OUT)
        # set motor pwm pin
        self.pwm = PWM(Pin(PWM_pin))
        # set PWM frequency
        self.pwm.freq(PWM_FREQ)
        # set duty cycle - 0=off
        self.pwm.duty_u16(0)
        # Current desired motor power
        self.base_power = 0
        # Current motor power w/ PD corrections
        self._power = 0
        # Motor bias for balancing
        self._bias = LEFT_MOTOR_BIAS if self.name == "left" else RIGHT_MOTOR_BIAS

    def _direction(self, power: int):
        "Power >= 0: forward else reverse"
        self.direction = Direction.FORWARD if power >= 0 else Direction.REVERSE
        return self.direction

    def _get_correction_dir(self, power):
        dir = self._direction(power)
        return 1 if dir == Direction.FORWARD else -1

    def _set_power(self, power: int, initial: bool = False):
        """Private method to set motor power & direction

        Args:
            - initial: bool - used to set the base_power if changing motor direction
                              PD should correct around base power.
        """
        if initial:
            self.base_power = power
        else:
            self._power = power
        direction = self._direction(power)
        self.mDir.value(direction)
        normalised_power = normalise_power(
            abs(power) - self._get_correction_dir(power) * self._bias
        )
        self.pwm.duty_u16(normalised_power)

    def correct_power(self, correction):
        "Method exposed for PD motor control corrections"
        new_power = self.base_power + (
            correction * self._get_correction_dir(self.base_power)
        )
        # For trace it still saves time being explicit
        if DEBUG:
            logger.log(
                "{} motor power: {}", self.name, new_power, level=LOG_LEVELS.TRACE
            )
        self._set_power(new_power)

    def off(self):
        self._set_power(0, True)

    def forward(self, power_level: int = ROBOT_SPEED):
        self._set_power(power_level, True)

    def reverse(self, power_level: int = ROBOT_SPEED):
        self._set_power(-power_level, True)


if __name__ == "__main__":
    left_motor = motorController(Motor.LEFT)
    right_motor = motorController(Motor.RIGHT)

    print("Forward")
    left_motor.forward()
    right_motor.forward()
    sleep_ms(1000)
    print("Reverse")
    left_motor.reverse()
    right_motor.reverse()
    sleep_ms(1000)
    left_motor.off()
    right_motor.off()
