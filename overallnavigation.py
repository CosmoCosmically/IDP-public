####################################################################################################
# Primary logic for the AGV
####################################################################################################

# ===================== MACHINE IMPORTS =====================
from grabber.components.state import GrabberState, LifterState
from grabber.components.types.resistance import Reel
from grabber.components.types.servo import ServoPositions
import micropython  # type: ignore
from machine import Timer  # type: ignore
from misc.components.LEDArray import LED_array
from navigation.config import REEL_DROP_NODE
from utime import ticks_ms, ticks_diff  # type: ignore
import uasyncio  # type: ignore
from misc.components.tof_VL53L0X import tofs

# ===================== LOCAL IMPORTS =====================
from navigation.components.navigation import navigation
from navigation.state import DropoffState, PathFollowingState

from grabber.components.grabberControl import grabberControl
from logger.logger import logger
from misc.components.button import button
from config import CONTROL_LOOP_POLL_RATE, LOG_LEVELS, RUN_TIME, END_FORWARD_TIME
from state import AGVState as State

# ===================== State =====================
state = State.REST

# ===================== NAVIGATION =====================
nav = navigation()
polls = 0
pickup_start = None
end_run_start = None
end_drop_node = None
second_pickup = False


# ===================== TIMER ISR =====================
def timer_isr(t):
    global polls
    polls += 1
    micropython.schedule(button._handler, t)
    micropython.schedule(nav._motion._handler, t)


# ===================== PICKUP / DROPOFF CONFIG =====================
pickup_bays = {
    "P1": True,
    "P2": False,  # We go there first
    "P3": True,
    "P4": True,
}


# ===================== PICKUP LOGIC =====================
def reset_pickups_if_empty():
    global second_pickup
    for bay in pickup_bays.keys():
        pickup_bays[bay] = True
    second_pickup = True


def nearest_pickup(start):
    if all(not free for free in pickup_bays.values()):
        # Reset free bays
        if second_pickup:
            logger.log("Done all 8 - stopping!")
            return None
        logger.log("AGV: resetting bays because none are free!")
        reset_pickups_if_empty()

    best_bay = None
    shortest = float("inf")

    for bay, free in pickup_bays.items():
        if not free:
            continue

        res = nav.get_directions(start, bay, nav.current_orientation)
        if res is None:
            logger.log("AGV: directions should not be None!")
            continue

        _, nodes, _ = res

        if len(nodes) < shortest:
            shortest = len(nodes)
            best_bay = bay

    if best_bay is not None:
        pickup_bays[best_bay] = False  # mark as used

    return best_bay


# ===================== PICKUP / DROPOFF LOGIC =====================

grabber = grabberControl()


# ===================== MAIN LOOP =====================
async def robot():
    global pickup_start
    global state
    global p_i
    global end_run_start
    global end_drop_node
    control_timer = Timer()
    control_timer.init(
        freq=CONTROL_LOOP_POLL_RATE,
        mode=Timer.PERIODIC,
        callback=timer_isr,
    )

    logger.log("Robot loop starting", LOG_LEVELS.INFO)
    start_time = ticks_ms()

    logger.log("tofs: Starting both tofs")

    tofs.start_tofs()

    while not button.state():
        if state == State.REST:
            # Go to the first pre-defined pickup
            logger.log("AGV: Starting - going to P2")
            nav.set_route("P2")
            state = State.MOVING_TO_PICKUP

        elif state == State.MOVING_TO_PICKUP:
            LED_array.strobe()
            nav.handler()
            if grabber.lifter._position != ServoPositions.LIFTER_DOWN:
                if pickup_start and ticks_diff(ticks_ms(), pickup_start) < 5000:
                    # In grace after last dropoff
                    pass
                else:
                    # Reset grabber 5s after dropoff
                    logger.log("Resetting grabber position after grace!")
                    # Set the position manually without inducing a state change
                    grabber._move_lifter(LifterState.DOWN, manual=True)
                    pickup_start = None
            if nav.state == PathFollowingState.COMPLETE:
                logger.log("AGV: At pickup bay")
                state = State.PICKING_UP

        elif state == State.PICKING_UP:
            # TODO: Align properly here
            grabber.handler()
            if grabber.state == GrabberState.REST:
                logger.log("AGV: Picking up reel")
                grabber.pickup()
                LED_array.flash()
            elif grabber.state == GrabberState.PICKED_UP:
                # Pick up done, nav-ing & transition state
                reel = grabber.reel
                LED_array.transition(reel)
                if reel is None:
                    # TODO: Change to default here
                    logger.log("AGV: Reel should not be None - panic!")
                    reel = Reel.REEL_0
                start_drop_node, end_drop_node = REEL_DROP_NODE[reel]
                nav.set_route(start_drop_node)
                # Reset the grabber
                grabber.reset()
                logger.log(
                    "AGV: Picked up - reset grabber & going to dropoff {} for reel {}",
                    start_drop_node,
                    reel,
                )
                state = State.MOVING_TO_DROPOFF

        elif state == State.MOVING_TO_DROPOFF:
            nav.handler()
            if nav.state == PathFollowingState.COMPLETE:
                logger.log("AGV: At start node for drop off bays")
                # Done with the route - prime dropoff
                nav.start_dropoff(end_drop_node)
                state = State.MOVING_TO_DROPOFF_BAY
                grabber._move_lifter(LifterState.UP, manual=True)

        elif state == State.MOVING_TO_DROPOFF_BAY:
            nav.dropoff_handler()
            if nav.state == DropoffState.COMPLETE:
                logger.log("AGV: At dropoff bay")
                state = State.DROPPING_OFF

        elif state == State.DROPPING_OFF:
            # We're now in position, physically drop the reel
            grabber.handler()
            if grabber.state == GrabberState.REST:
                logger.log("AGV: Dropping off reel")
                grabber.dropoff()
                LED_array.flash()
            elif grabber.state == GrabberState.DROPPED_OFF:
                LED_array.off()
                # Drop off done, nav-ing & transition state
                if ticks_diff(ticks_ms(), start_time) > RUN_TIME:
                    # Run out of time, nav to start
                    # TODO: Do we have to go back to start within 6 min?
                    logger.log("AGV: Ran out of time, going back to the start box!")
                    nav.set_route("S")
                    state = State.ENDING_RUN
                    continue
                pickup_node = nearest_pickup(nav.current_node)
                if pickup_node is not None:
                    nav.set_route(pickup_node)
                    state = State.MOVING_TO_PICKUP
                    # Get the start time for the nav to next pickup
                    pickup_start = ticks_ms()
                    # Reset the grabber
                    grabber.reset()
                    logger.log(
                        "AGV: Dropped off - Reset grabber & going to pickup {}",
                        pickup_node,
                    )
                else:
                    logger.log("AGV: No available pickup node found!", LOG_LEVELS.INFO)
                    # TODO: put default here
                    state = State.ENDING_RUN
                    continue

        elif state == State.ENDING_RUN:
            nav.handler()
            LED_array.flash()
            if nav.state == PathFollowingState.COMPLETE:
                logger.log("AGV: Back at start bay")
                nav._motion._forward(50)
                end_run_start = ticks_ms()
                if (
                    end_run_start
                    and ticks_diff(ticks_ms(), end_run_start) > END_FORWARD_TIME
                ):
                    nav._motion.stop()
                    logger.log("AGV: Positioned nicely in start bay, goodbye!")
                    break

        await uasyncio.sleep_ms(1000 // CONTROL_LOOP_POLL_RATE)

    nav._motion.stop()
    tofs.stop_tofs()
    control_timer.deinit()

    logger.log("polls: {}", str(polls))
    logger.log("Robot loop done", LOG_LEVELS.INFO)
    logger.close()
