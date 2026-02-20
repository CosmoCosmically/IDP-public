####################################################################################################
#
# Primary logic for the AGV
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# Machine imports
import micropython  # type: ignore
from machine import Timer  # type: ignore
from navigation.state import NavigationState, PathFollowingState
from utime import ticks_ms, ticks_diff  # type: ignore
import uasyncio  # type: ignore

# Local imports
from navigation.components.navigation import navigation
from logger.logger import logger
from misc.components.button import button
from config import CONTROL_LOOP_POLL_RATE, LOG_LEVELS, RUN_TIME, DEBUG
from state import AGVState as State

# Navigation
nav = navigation()
polls = 0


state = State.REST
transition = False

last_nav_time = ticks_ms()


def timer_isr(t):
    # TODO: Not permanent just for testing
    global polls
    polls += 1
    micropython.schedule(nav._motion._handler, t)
    micropython.schedule(button._handler, t)


async def robot():  # Background handling of PD / junction detection
    global state

    control_timer = Timer()
    control_timer.init(
        freq=CONTROL_LOOP_POLL_RATE, mode=Timer.PERIODIC, callback=timer_isr
    )

    if DEBUG:
        logger.log("Robot loop starting: hello!", LOG_LEVELS.INFO)

    start_time = ticks_ms()
    while not button.state() and ticks_diff(ticks_ms(), start_time) < RUN_TIME:
        if state == State.REST:
            # Go to the first pickup
            nav.set_route("P1")
            state = State.MOVING_TO_PICKUP
        elif state == State.MOVING_TO_PICKUP:
            nav.handler()
            if nav.state == PathFollowingState.REST:
                # Done with the route
                state = State.PICKING_UP
        elif state == State.PICKING_UP:
            # if pickup_handler.state is Done:
            # Done picking up, go to the correct node for the reel
            # reel_type = pickup_handler.reel_type
            # dest = REEL_DROP_NODE[reel_type]
            logger.log("AGV: setting J28")
            nav.set_route("J5")
            nav.handler()
            state = State.MOVING_TO_DROPOFF
        elif state == State.MOVING_TO_DROPOFF:
            nav.handler()
            if nav.state == PathFollowingState.REST:
                # Done with the route
                state = State.DROPPING_OFF
        elif state == State.DROPPING_OFF:
            # if dropoff_handler.state is Done:
            # Done dropping off, go to the next pickup
            # if next_pickup is None:
            # Picked up all 4 reels, reset
            # state = State.REST
            # return
            # next_pickup = closest_pickup() # nav command?
            # nav.set_route(next_pickup)
            # state = State.MOVING_TO_PICKUP
            pass

        await uasyncio.sleep_ms(1000 // CONTROL_LOOP_POLL_RATE)

    if DEBUG:
        logger.log("polls: {}", str(polls))
        logger.log("poll rate: {}{}", str((polls * 1000) / RUN_TIME), "Hz")

    control_timer.deinit()
    if DEBUG:
        logger.log("Robot loop done: goodbye!", LOG_LEVELS.INFO)
    logger.close()
