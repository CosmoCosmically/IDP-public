####################################################################################################
#
# Logic related to the motion control.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# Machine imports
from config import LOG_LEVELS
from navigation.components.types.navigation import JunctionOptions
from utime import ticks_ms, ticks_diff  # type: ignore

# Local imports
from navigation.state import LineState
from navigation.components.motorController import motorController
from navigation.components.PDControl import PDControl
from navigation.components.lineSensor import lineSensorArray
from navigation.components.utils.motionControl import junction_detection, line_detection
from logger.logger import logger
from navigation.config import (
    JUNCTION_TURN_GRACE_PERIOD,
    ROBOT_SPEED,
    JUNCTION_FORWARD_TIME,
    REVERSE_GRACE_MULTIPLIER,
    PD,
)

# Type imports
from navigation.components.types.motor import Motor

# State import
from navigation.state import MotionState as State


class motion:
    """
    High-level motion state machine coordinating line following,
    junction handling, turning, and PD-based correction.
    """
    def __init__(self):
        self.pd = PDControl()

        self.left = motorController(motor=Motor.LEFT)
        self.right = motorController(motor=Motor.RIGHT)
        self.lsa = lineSensorArray()

        self._state = State.REST
        # TODO: Could automatically set start on state transition
        self.state_transition: bool = False
        self.line_state = None

        # TODO: Maybe collapse into a junction state dict or similar
        self.junction_start = None
        self.junction_turn_start = None
        self.junction_turn_type = None
        self.last_turn_time = None
        self.u_turn_counter = 0

        self.reversing = False

    @property
    def state(self):
        """
        Current motion state.
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Transition motion state and flag a state change.
        """
        self.state_transition = True
        self._state = state

    def forward(self, power: int = ROBOT_SPEED):
        """
        Command the robot to move forward while following the line.
        """
        logger.log("Motion: Received forward command", level=LOG_LEVELS.DEBUG)
        self.state = State.FOLLOWING_LINE
        self.reversing = False
        self._forward(power)

    def reverse(self, power: int = ROBOT_SPEED):
        """
        Command the robot to reverse while following the line.
        """
        logger.log("Motion: Received reverse command", level=LOG_LEVELS.DEBUG)
        self.state = State.FOLLOWING_LINE
        self.reversing = True
        self._reverse(power)

    def stop(self):
        """
        Immediately stop both motors and enter REST state.
        """
        logger.log("Motion: Received stop command", level=LOG_LEVELS.DEBUG)
        self.state = State.REST
        self._stop()

    def turn_left(self, power: int = ROBOT_SPEED):
        """
        Execute a left turn at a junction.
        """
        logger.log(
            "Motion: Received left command",
            level=LOG_LEVELS.DEBUG,
        )
        # Get a start time for the junction grace period
        self.junction_turn_start = ticks_ms()
        self.junction_turn_type = JunctionOptions.GO_LEFT
        self.left.reverse(power)
        logger.log("Motion: left {} {}", self.junction_turn_start, self.state)
        self.right.forward(power)

    def turn_right(self, power: int = ROBOT_SPEED):
        """
        Execute a right turn at a junction.
        """
        logger.log("Motion: Received right command", level=LOG_LEVELS.DEBUG)
        # Get a start time for the junction grace period
        self.junction_turn_start = ticks_ms()
        self.junction_turn_type = JunctionOptions.GO_RIGHT
        logger.log("Motion: right {} {}", self.junction_turn_start, self.state)
        self.left.forward(power)
        self.right.reverse(power)

    def continue_straight(self, power: int = ROBOT_SPEED):
        """
        Continue straight through a junction.
        """
        logger.log("Motion: Received continue straight command", level=LOG_LEVELS.DEBUG)
        # Get a start time for the junction grace period
        self.junction_turn_start = ticks_ms()
        self.junction_turn_type = JunctionOptions.GO_STRAIGHT
        self._forward(power)

    def u_turn(self, power: int = ROBOT_SPEED, opposite=False):
        """
        Execute a U-turn at a junction.

        Args:
            power (int): Turn power.
            opposite (bool): Reverse turning direction if True.
        """
        # TODO: This only works at a junction, not on a line (probably fine)
        logger.log("Motion: Received u_turn command", level=LOG_LEVELS.DEBUG)
        self.junction_turn_start = ticks_ms()
        self.junction_turn_type = JunctionOptions.U_TURN
        if not opposite:
            self.left.reverse(power)
            self.right.forward(power)
        else:
            self.left.forward(power)
            self.right.reverse(power)

    ############# PRIVATE METHODS - DO NOT USE OUTSIDE #############

    def _forward(self, power: int = ROBOT_SPEED):
        """
        Internal motor drive: set both motors forward and apply PD tunings.
        """
        logger.log("Motion: internal forward", level=LOG_LEVELS.DEBUG)
        self.pd.pd.tunings = (PD.KP, PD.KI, PD.KD)
        self.left.forward(power)
        self.right.forward(power)

    def _reverse(self, power: int = ROBOT_SPEED):
        """
        Internal motor drive: set both motors in reverse and apply PD tunings.
        """
        logger.log("Motion: internal reverse", level=LOG_LEVELS.DEBUG)
        self.pd.pd.tunings = (PD.KP * 0.25, PD.KI, PD.KD * 0.25)
        self.left.reverse(power)
        self.right.reverse(power)

    def _stop(self):
        """
        Internal stop: set both motors to zero power.
        """
        logger.log("Motion: internal stop", level=LOG_LEVELS.DEBUG)
        self.left.forward(0)
        self.right.forward(0)

    def _turn_handle(self):
        """
        Internal handler to prime state for turn execution.
        """
        self.state = State.JUNCTION

    def _update_pd(self, lsrs):
        """
        Internal: Update motor powers using PD correction based on line sensor readings.
        """
        correction = self.pd.calculate_correction(lsrs)
        self.left.correct_power(-correction)
        self.right.correct_power(correction)

    def _update(self, lsrs, o_t):
        """
        Internal: Handle line following and junction detection logic.
        """
        lo, _, _, ro = lsrs
        # Ignore inner sensors for junction detection
        # ONLY true if not already triggered and current reading is 1
        self.junction_start = junction_detection((lo or ro) and not o_t)

        if self.junction_start is not None:
            # We're at a junction, set PRE_JUNCTION state & crawl forward with the robot until nav decides what to do
            self.state = State.PRE_JUNCTION
            # TODO: Tune power
            self._forward()
            logger.log(
                "Motion: detected junction, crawling {}",
                lsrs,
                level=LOG_LEVELS.DEBUG,
            )
            return
        self._update_pd(lsrs)

    def _line_detection(self, lsrs, i_t):
        """
        Internal: Detect line state during junction handling and update state accordingly.
        """
        _, li, ri, _ = lsrs
        # Straight doesn't turn so accept either line sensor
        self.line_state = line_detection(
            li, ri, i_t, self.junction_turn_type, self.junction_turn_start
        )
        if self.line_state == LineState.CENTERED:
            if (
                self.junction_turn_type == JunctionOptions.U_TURN
                # TODO: probably done u-turn: TIME!!!!
            ):
                if (
                    ticks_diff(ticks_ms(), self.junction_turn_start)
                    < JUNCTION_TURN_GRACE_PERIOD * 2.5
                ):
                    return
            logger.log("Motion: successful junction {}", lsrs, level=LOG_LEVELS.DEBUG)
            # Stop turning
            # TODO: Quick enough we don't need this?
            #       Could add a better handler to just start on the next command
            # self._stop()
            self.last_turn_time = ticks_ms()
            self.junction_turn_type = None
            self.junction_turn_start = None
            self.u_turn_counter = 0
            self.state = State.FOLLOWING_LINE

    def _handler(self, _):
        """
        Internal: Main state handler for motion state machine.
        """
        if self.state_transition:
            # Reset the PD controller on state transition
            self.pd.reset()
            self.state_transition = False

        if self.state == State.REST:
            # Nothing to do
            return

        # Get fresh line sensor values
        lsrs = self.lsa.state()
        o_t, i_t = self.lsa.rising_edge
        if self.state == State.FOLLOWING_LINE:
            # No junction, keep moving & correcting
            self._update(lsrs, o_t)
        elif self.state == State.PRE_JUNCTION:
            lo, _, _, ro = lsrs
            # Either both see black OR threshold reached...
            # TODO: Test!
            diff = ticks_diff(ticks_ms(), self.junction_start)
            # Increase when reversing due to geometry
            # TODO: Might need grace for the lower timeout?
            grace_mult = REVERSE_GRACE_MULTIPLIER if self.reversing else 1
            if diff > JUNCTION_FORWARD_TIME * grace_mult:
                # Aligned in the forwards direction, transition to TURN
                logger.log(
                    "Motion control: Transitioning from PRE_JUNCTION to JUNCTION after grace! {}",
                    lsrs,
                    level=LOG_LEVELS.DEBUG,
                )
                self.state = State.JUNCTION
                # TODO: Might not be necessary?
                # self._stop()
        elif self.state == State.JUNCTION:
            # Junction, go into line detection mode
            # self.junction_turn_start might be None here but that's fine
            self._line_detection(lsrs, i_t)
        # Update rising edge detection - last so we don't miss it!
        self.lsa.update_rising_edge()


# TODO: Could add recovery state here?
