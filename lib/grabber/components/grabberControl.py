####################################################################################################
#
# Logic related to the grabber control.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################rom utime import sleep_ms  # type: ignore

from config import LOG_LEVELS

from grabber.components.resistanceSensing import resistanceSensing
from logger.logger import logger
from grabber.components.servoController import servoController
from grabber.components.types.servo import Servo
from grabber.config import ServoPositions
from grabber.components.state import (
    DropOffState,
    GrabberState as State,
    ResistanceSenseState,
)
from grabber.components.state import JawState, LifterState, PickUpState, ServoState


class grabberControl:
    def __init__(self):
        self.jaw = servoController(Servo.GRABBER)
        self.lifter = servoController(Servo.LIFTER)
        self._turn_start = None
        self._state = State.REST
        self._pickup_state = PickUpState.NONE
        self._dropoff_state = DropOffState.NONE
        self._i = 0
        self._r = resistanceSensing()
        self._reel = None

        # Reset arm state on start
        self._move_jaw(JawState.OPEN, True)
        self._move_lifter(LifterState.DOWN, True)

    @property
    def reel(self):
        return self._reel

    @property
    def state(self):
        return self._state

    # TODO: This is so we don't just have PICKED_UP / DROPPED_OFF be a one tick,
    #       it'd work but we would need very careful handling
    def reset(self):
        "Reset the grabber."
        logger.log("Grabber: Resetting the grabber!")
        self._state = State.REST

    def _move_lifter(self, position: str, manual=False):
        """Request that the lifter moves up / down

        Args:
            position: LifterState - either UP or DOWN
        """
        if position == LifterState.UP:
            servo_pos = ServoPositions.LIFTER_UP
        elif position == LifterState.MID:
            servo_pos = ServoPositions.LIFTER_MID
        else:
            servo_pos = ServoPositions.LIFTER_DOWN
        logger.log("Grabber: Moving lifter {}", position, LOG_LEVELS.DEBUG)
        self.lifter.set_position(servo_pos, manual)

    def _move_jaw(self, position: str, manual=False):
        """Request that the jaw opens / closes

        Args:
            position: LifterState - either OPEN or CLOSED
        """
        logger.log("Grabber: Moving jaw {}", position, LOG_LEVELS.DEBUG)
        position = (
            ServoPositions.JAW_OPEN
            if position == JawState.OPEN
            else ServoPositions.JAW_CLOSED
        )
        self.jaw.set_position(position, manual)

    def pickup(self):
        logger.log("Grabber: Picking up reel")
        "Pick up a reel when at a pickup bay & aligned."
        self._state = State.PICKING_UP

    def dropoff(self):
        logger.log("Grabber: Dropping off reel")
        "Drop off a reel when at a dropoff bay & aligned."
        self._state = State.DROPPING_OFF

    def handler(self):
        if self.state == State.REST:
            # Nothing to do
            return
        self.jaw._handler()
        self.lifter._handler()

        if self.state == State.PICKING_UP:
            if self._pickup_state == PickUpState.NONE:
                self._pickup_state = PickUpState.CLOSING_JAW
                self._move_jaw(JawState.CLOSED)
            elif self._pickup_state == PickUpState.CLOSING_JAW:
                if self.jaw.state == ServoState.IN_POSITION:
                    # Done with closing jaw, start to measure resistance and raise arm
                    self._r.start_sense()
                    self._pickup_state = PickUpState.RAISING_LIFTER
                    self._move_lifter(LifterState.MID)
            elif self._pickup_state == PickUpState.RAISING_LIFTER:
                self._r._handler()
                if (
                    self.lifter.state == ServoState.IN_POSITION
                    and self._r.state == ResistanceSenseState.DETECTED
                ):
                    # Done with lifting & sensing resistance, transition state to PICKED_UP & reset _pickup_state
                    self._reel = self._r._reel
                    self._r.reset()
                    self._state = State.PICKED_UP
                    self._pickup_state = PickUpState.NONE

        elif self.state == State.DROPPING_OFF:
            if self._dropoff_state == DropOffState.NONE:
                # Start the sequence
                self._dropoff_state = DropOffState.OPENING_JAW
                self._move_jaw(JawState.OPEN)
            elif self._dropoff_state == DropOffState.OPENING_JAW:
                if self.jaw.state == ServoState.IN_POSITION:
                    # Done with opening jaw, transition stated to DROPPED_OFF & reset _pickup_state
                    self._state = State.DROPPED_OFF
                    self._dropoff_state = DropOffState.NONE
