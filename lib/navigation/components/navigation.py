####################################################################################################
#
# Logic related to navigation.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# Machine imports
from misc.state import ToFState
from navigation.config import DROP_OFF_FORWARD_TIME, NODE_MAP
from utime import ticks_diff, ticks_ms  # type: ignore

# Local imports
from config import LOG_LEVELS
from logger.logger import logger
from navigation.components.motionControl import motion
from navigation.components.pathfinding import pathfinding
from misc.components.tof_VL53L0X import tofs

# Type imports
from navigation.components.types.navigation import JunctionOptions

# State imports
from navigation.state import (
    NavigationState as State,
    PathFollowingState,
    DropoffState,
    MotionState,
)


class navigation:
    def __init__(self):
        self._pathfinding = pathfinding()
        self._motion = motion()
        self._state = State.FOLLOWING_PATH
        self._path_following_state = PathFollowingState.REST
        self._dropoff_state = DropoffState.REST
        self._dropoff_start = None

        self.route = None
        self.start_node = None
        self.current_node: str = "START_BOX"
        self.current_orientation: str = "N"
        self.dropoff_initial = True
        self.go_back_to_nav = False
        self.end_drop_node = None

        self.bay_occ = False
        self.delivered_bays = set()

        self.motion_mapping = {
            JunctionOptions.GO_LEFT: self._motion.turn_left,
            JunctionOptions.GO_RIGHT: self._motion.turn_right,
            JunctionOptions.GO_STRAIGHT: self._motion.continue_straight,
            JunctionOptions.U_TURN: self._motion.u_turn,
        }

        self.NODE_MAP = NODE_MAP

    @property
    def state(self):
        "Returns the state depending on which mode we're in."
        return (
            self._path_following_state
            if self._state == State.FOLLOWING_PATH
            else self._dropoff_state
        )

    def _route_gen(self, route, path):
        # We correlate the current instruction with the NEXT node rather than current hence 1:
        for step, node in zip(route, path[1:]):
            yield (step, node)

    def get_directions(self, start: str, dest: str, orientation: str):
        return self._pathfinding.get_directions(start, dest, orientation)

    def set_route(
        self,
        dest: str,
        start: str | None = None,  # type: ignore
        orientation: str | None = None,  # type: ignore
    ):
        # Update states based on the route we're setting
        self._state = State.FOLLOWING_PATH
        self._path_following_state = PathFollowingState.NAVIGATING

        orientation = orientation or self.current_orientation
        start_node = start or self.current_node
        logger.log("Pathfinding: {} {} {}", start_node, dest, orientation)
        res = self._pathfinding.get_directions(start_node, dest, orientation)
        if res is None:
            # Panic!
            return
        last_orientation, nodes, route = res

        if not last_orientation:
            logger.log("Navigation - last_orientation is None?!")
            # Panic!
            last_orientation = "N"
        self.start_node = start_node
        self.current_node = dest
        self.current_orientation = last_orientation
        logger.log(
            "Navigation: setting route {}, path {}, ori",
            route,
            nodes,
            self.current_orientation,
        )
        self.route = self._route_gen(route, nodes)
        # Get to first junction - if a drop off or pick up then reverse out
        if start_node.startswith(("D", "P")):
            self._motion.reverse()
        else:
            self._motion.forward()

    def get_tof_type(self):
        if not self.current_node.startswith("J"):
            return "right"  # right  # or raise error

        num = int(self.current_node[1:])  # extract number after J

        if 1 <= num <= 6 or 19 <= num <= 24:
            return "right"  # right
        elif 7 <= num <= 12 or 13 <= num <= 18:
            return "left"  # left
        else:
            return "right"  # fallback #right

    def start_dropoff(self, end_drop_node):
        "Go into the NAVIGATING state for dropoff"
        self._state = State.DROPOFF
        self._dropoff_state = DropoffState.NAVIGATING
        self.dropoff_initial = True
        self.end_drop_node = end_drop_node
        logger.log("Starting dropoff {} {}", self._state, self._dropoff_state)

    def dropoff_handler(self):
        "Specialised handler for when we're in the delivery area."
        if self.state == DropoffState.NAVIGATING:
            # Need to find an empty bay - check in pre-junction!
            if self.dropoff_initial or self._motion.state == MotionState.PRE_JUNCTION:
                logger.log("Navigation - dropoff: In PRE_JUNCTION, checking ToFs!")
                # Check because reel is invisible to ToF
                if self.current_node == self.end_drop_node:
                    # Override, just turn in
                    self.bay_occ = False
                elif self.current_node in self.delivered_bays:
                    # already has a reel
                    self.bay_occ = True
                else:
                    if tofs.state == ToFState.REST:
                        tofs.start_reading()
                        logger.log(
                            "Navigation - dropoff - selected ToF is {}",
                            self.get_tof_type(),
                        )
                    tofs.handler(self.get_tof_type())
                    if tofs.state == ToFState.ACQUIRING_READINGS:
                        # Not done yet
                        return
                    elif tofs.state == ToFState.COMPLETE:
                        # Done reading, get occupied
                        self.bay_occ = tofs.occupied
                        logger.log(
                            "Navigation - dropoff: ToFs complete bay is occ: {}",
                            self.bay_occ,
                        )
                        tofs.reset()
                logger.log("Navigation - dropoff: bay occ {}", self.bay_occ)
                self._dropoff_state = DropoffState.TURN_PENDING

        elif self.state == DropoffState.TURN_PENDING:
            # We start at the first junction so we'd already effectively be in junction mode
            if self.dropoff_initial or self._motion.state == MotionState.JUNCTION:
                self.dropoff_initial = False
                # Update current node & direction for pathfinding later
                if self.bay_occ:
                    self.bay_occ = False
                    logger.log(
                        "Navigation - dropoff: Bay is full! Going to next.",
                    )
                    junction_dir = JunctionOptions.GO_STRAIGHT
                    self.go_back_to_nav = True
                else:
                    self.go_back_to_nav = False
                    cardinal_dir = NODE_MAP[self.current_node].get("dropoff", None)
                    if cardinal_dir is None:
                        logger.log(
                            "Navigation - dropoff: Bay dropoff is None when it really shouldn't be!"
                        )
                        # Fallback
                        junction_dir = JunctionOptions.GO_STRAIGHT
                        self._dropoff_state = DropoffState.NAVIGATING
                    else:
                        junction_dir, orientation = pathfinding.compute_turn(
                            self.current_orientation, cardinal_dir
                        )
                        logger.log(
                            "Navigation - dropoff: Turning into bay {} {}",
                            orientation,
                            junction_dir,
                        )
                        # We've turned into a bay so bay will be full
                        self.delivered_bays.add(self.current_node)
                        if junction_dir is None or orientation is None:
                            # Panic!
                            logger.log("Navigation - dropoff: Compute turn failed!")
                            junction_dir = JunctionOptions.GO_STRAIGHT
                        # Update orientation
                        self.current_orientation = (
                            orientation or self.current_orientation
                        )
                # Update position
                self.current_node = NODE_MAP[self.current_node][
                    self.current_orientation
                ]
                self._dropoff_state = DropoffState.TURNING
                logger.log("Navigation - dropoff: Executing command {}", junction_dir)
                motion_cmd = self.motion_mapping[junction_dir]
                motion_cmd()

        elif self._dropoff_state == DropoffState.TURNING:
            if self._motion.state == MotionState.REST:
                self._motion._turn_handle()
            if self._motion.state == MotionState.FOLLOWING_LINE:
                logger.log(
                    "Navigation - dropoff: Turning complete, going forward & state NAVIGATING",
                    level=LOG_LEVELS.DEBUG,
                )
                # Done with the turn - enter the dropoff handling
                self._motion.forward(60)
                if self.go_back_to_nav:
                    self._dropoff_state = DropoffState.NAVIGATING
                    self.go_back_to_nav = False
                else:
                    self._dropoff_state = DropoffState.DROPPING_OFF
                self._dropoff_start = ticks_ms()

        elif self._dropoff_state == DropoffState.DROPPING_OFF:
            # Align with the bay - we're already going forward
            if (
                self._dropoff_start is not None
                and ticks_diff(ticks_ms(), self._dropoff_start) > DROP_OFF_FORWARD_TIME
            ):
                self._motion.stop()
                logger.log("Navigation - dropoff: In position!")
                # We're done, reset state
                self._dropoff_start = None
                self.end_drop_node = None
                self._dropoff_state = DropoffState.COMPLETE

    def handler(self):
        if self.state == PathFollowingState.NAVIGATING:
            if self._motion.state == MotionState.JUNCTION:
                logger.log(
                    "Navigation: Entering junction handling", level=LOG_LEVELS.DEBUG
                )
                # Junction detected, execute the next step
                if self.route is None or (step_node := next(self.route, None)) is None:
                    # Exhausted commands, we're done with the defined route
                    self._path_following_state = PathFollowingState.COMPLETE
                    self._motion.stop()
                    logger.log("Navigation: Completed route", level=LOG_LEVELS.DEBUG)
                    self.route = None
                    return

                logger.log(
                    "Navigation: Getting next step in route", level=LOG_LEVELS.DEBUG
                )
                # We need to handle the junction - match action to motion command
                step, next_node = step_node
                self.pending_node = next_node
                motion_cmd = self.motion_mapping[step]

                logger.log("Navigation: next node {}", next_node)

                logger.log("Navigation: Executing the command", level=LOG_LEVELS.DEBUG)
                if self.start_node == "P4" and step == JunctionOptions.U_TURN:
                    motion_cmd(opposite=True)  # type: ignore
                else:
                    motion_cmd()
                self._path_following_state = PathFollowingState.TURNING

        elif self._path_following_state == PathFollowingState.TURNING:
            # Can also check for LINE_DETECTED if we want to slow down turn
            if self._motion.state == MotionState.FOLLOWING_LINE:
                logger.log(
                    "Navigation: Turning complete, going forward & state NAVIGATING",
                    level=LOG_LEVELS.DEBUG,
                )
                # Done with the turn - go forward as usual
                self._path_following_state = PathFollowingState.NAVIGATING
                self._motion.forward()
            else:
                return
