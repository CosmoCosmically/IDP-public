####################################################################################################
#
# Logic related to the servo control.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

from machine import Pin, PWM  # type: ignore
import uasyncio  # type: ignore
from utime import ticks_diff, ticks_ms  # type: ignore

from misc.components.button import button
from grabber.components.state import ServoState as State
from grabber.config import POS_TO_PULSE_WIDTH, SERVO_POLL_RATE, SERVO_TURN_TIME
from grabber.components.types.servo import ServoPositions
from grabber.components.utils.servo import pulse_width_to_pwm
from grabber.components.types.servo import Servo
from logger.logger import logger

SERVO = {
    Servo.GRABBER: {"name": "grabber", "PWM": 13},
    Servo.LIFTER: {"name": "lifter", "PWM": 15},
}


class servoController:
    def __init__(self, servo: int):
        """Initiate a servo controller for a servo

        Args: servo - Servo: servo we want to control
        """
        servo_info = SERVO[servo]
        self.name, PWM_pin = (
            servo_info["name"],
            servo_info["PWM"],
        )
        # self.pos = ADC(pos_pin)
        # set servo direction pin
        self.pwm = PWM(
            Pin(PWM_pin), freq=SERVO_POLL_RATE, duty_u16=pulse_width_to_pwm(1500)
        )
        # Current servo position
        self._position = 0
        # Current state
        self._state = State.REST
        self._turn_start_time = None

    def _set_position(self, pulse_width: int):
        """Private method to set servo power"""
        self.pwm.duty_u16(pulse_width_to_pwm(pulse_width))

    def set_position(self, position: int, manual=False):
        "Set the position, prevent state change if manual."
        if not manual:
            self.state = State.TURNING
        self._turn_start_time = ticks_ms()
        self._position = position
        logger.log(
            "Servo controller: Setting servo {} to position {}, pulse width {}, pwm {}",
            self.name,
            position,
            POS_TO_PULSE_WIDTH[position],
            pulse_width_to_pwm(POS_TO_PULSE_WIDTH[position]),
        )
        self._set_position(POS_TO_PULSE_WIDTH[position])

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    # TODO: For precise control, servo needs tuning!
    def _handler(self):
        if self.state == State.TURNING:
            if (
                self._turn_start_time is not None
                and ticks_diff(ticks_ms(), self._turn_start_time) > SERVO_TURN_TIME
            ):
                logger.log("Servo controller: Servo probably in position")
                # Reset turn time
                self.state = State.IN_POSITION
                self._turn_start_time = None
                # TODO: No idea what to do if this happens, just keep trying??


async def main():
    grabber_servo = servoController(Servo.GRABBER)
    lifter_servo = servoController(Servo.LIFTER)
    lifter_servo.set_position(ServoPositions.MID)
    grabber_servo.set_position(ServoPositions.MID)
    await uasyncio.sleep_ms(2500)
    lifter_servo.set_position(ServoPositions.LIFTER_DOWN)
    grabber_servo.set_position(ServoPositions.JAW_OPEN)
    await uasyncio.sleep(5)
    grabber_servo.set_position(ServoPositions.JAW_CLOSED)
    await uasyncio.sleep(5)
    lifter_servo.set_position(ServoPositions.LIFTER_UP)
    await uasyncio.sleep(5)
    grabber_servo.set_position(ServoPositions.JAW_OPEN)
    return
    print("Disconnect arm / rod from servos now! 15s grace to prevent damage")
    await uasyncio.sleep_ms(15000)
    print("Setting grabber servo to mid position & waiting 5s")
    grabber_servo.set_position(ServoPositions.MID)
    await uasyncio.sleep_ms(5000)
    print("Setting lifter servo to mid position & waiting 5s")
    lifter_servo.set_position(ServoPositions.MID)
    await uasyncio.sleep_ms(5000)
    print("If servos are wrong way round, flip wires now!")
    print("Now physically attach lifter so grabber is horizontal")
    print("And grabber so plate is roughly mid way through rotation")
    print("When done, click button")
    while True:
        button._handler(0)
        if button.state():
            break
        await uasyncio.sleep_ms(50)
    print("OK, now slowly lowering arm. Click button when in bottom position")
    print("Note: if it goes the wrong way, click button and ignore first value")
    s_pw = 1500
    i = 0
    while True:
        lifter_servo._set_position(s_pw + i * 5)
        button._handler(0)
        if button.state():
            print("Pulse width at stop: {}", s_pw + i * 5)
            break
        await uasyncio.sleep_ms(50)
        i += 1
    print("OK, resetting arm to the centre")
    lifter_servo.set_position(ServoPositions.MID)
    await uasyncio.sleep_ms(1000)
    print("Now raising arm if it went the wrong way before")
    i = 0
    while True:
        lifter_servo._set_position(s_pw - i * 5)
        button._handler(0)
        if button.state():
            print("Pulse width at stop: {}", s_pw + i * 5)
            break
        await uasyncio.sleep_ms(50)
        i += 1
    print("OK, now slowly opening jaw. Click button when in max open position")
    print("Note: if it goes the wrong way, click button and ignore first value")
    s_pw = 1500
    i = 0
    while True:
        grabber_servo._set_position(s_pw + i * 5)
        button._handler(0)
        if button.state():
            print("Pulse width at stop: {}", s_pw + i * 5)
            break
        await uasyncio.sleep_ms(50)
        i += 1
    print("OK, resetting jaw to the centre")
    grabber_servo.set_position(ServoPositions.MID)
    await uasyncio.sleep_ms(1000)
    print("Now slowly closing jaw (or opening if inital was closing)")
    i = 0
    while True:
        grabber_servo._set_position(s_pw - i * 5)
        button._handler(0)
        if button.state():
            print("Pulse width at stop: {}", s_pw + i * 5)
            break
        await uasyncio.sleep_ms(50)
        i += 1
    print("Tuning complete!")


if __name__ == "__main__":
    uasyncio.run(main())
