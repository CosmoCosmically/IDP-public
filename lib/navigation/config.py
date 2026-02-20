####################################################################################################
#
# Navigation config for the AGV code.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# upp - upload program
# rp - run program
# rmp - delete all files off pico

from grabber.components.types.resistance import Reel

ROBOT_SPEED = 95

# TODO: Need to redo with new weight distro!
LEFT_MOTOR_BIAS = 0
RIGHT_MOTOR_BIAS = 0

# +-60% of motor speed
MAX_PD_CORRECTION = 80


# TODO: KP too high, TUNE!
# https://robotresearchlab.com/2019/02/16/pid-line-follower-tuning/
# TLDR;
# Apparently max_speed = error * kp is a good starting point
# Which would equal a KP of 50
# KD apparently should be KP*(10-20) (!) as a starting value
# so KD = 200 would be better as a test ..?!
class PD:
    KP = 200
    KI = 0
    KD = 0


class LineSensor:
    OUTER_LEFT = 3
    INNER_LEFT = 2
    INNER_RIGHT = 1
    OUTER_RIGHT = 0


# TODO: Use - DEPENDENT ON ROBOT_SPEED, IF ROBOT_SPEED CHANGES CHANGE THESE!
# This is incredibly arbitrary currently
# (Hint: non-dimensionalise?)
# This wouldn't be necessary if we had the outer line sensors along the wheel
# axis as the front line sensors would already be sufficiently offset.
JUNCTION_FORWARD_TIME = 135

# TODO: Per log files this could potentially be lowered
JUNCTION_STRAIGHT_GRACE_PERIOD = 150
# TODO: From the log files a turn takes ~ 570ms
JUNCTION_TURN_GRACE_PERIOD = 450

# Reverse needs a little longer at junctions
# TODO: 1.5?
REVERSE_GRACE_MULTIPLIER = 1.25

# TODO: Entirely arbitrary, needs a lot of testing to prevent collision
# Or sensor input
DROP_OFF_FORWARD_TIME = 1550


### Dropoff logic for a given reel type

# TODO: This should work unless pathfinding does something really stupid (it shouldn't ever)
#       Finalise with correct nodes!
REEL_DROP_NODE = {
    Reel.REEL_0: ("J1", "J6"),  # GREEN!
    Reel.REEL_1: ("J7", "J12"),  # YELLOW!
    Reel.REEL_2: ("J13", "J18"),  # BLUE!
    Reel.REEL_3: ("J19", "J24"),  # RED!
}


NODE_LIST = [
    "START_BOX",
    "S",
    # Pickup spots
    "P1",
    "P2",
    "P3",
    "P4",
    # Junctions
    "J1",
    "J2",
    "J3",
    "J4",
    "J5",
    "J6",
    "J7",
    "J9",
    "J10",
    "J11",
    "J12",
    "J13",
    "J14",
    "J15",
    "J16",
    "J17",
    "J18",
    "J19",
    "J20",
    "J21",
    "J22",
    "J23",
    "J24",
    "J25",
    "J26",
    "J27",
    "J28",
    "J29",
    "J30",
    "J31",
    "J32",
    "J33",
    "J34",
    "J35",
    "J36",
    "J37",
    # Dropoff locations
    "D1",
    "D2",
    "D3",
    "D4",
    "D5",
    "D6",
    "D7",
    "D8",
    "D9",
    "D10",
    "D11",
    "D12",
    "D13",
    "D14",
    "D15",
    "D16",
    "D17",
    "D18",
    "D19",
    "D20",
    "D21",
    "D22",
    "D23",
    "D24",
]

NODE_MAP = {
    # Start box - not a real node but useful to have
    "START_BOX": {"N": "S", "E": None, "S": None, "W": None},
    "S": {"N": "J29", "E": None, "S": None, "W": None},
    # Junctions J1–J35
    "J1": {"N": "J2", "E": "D1", "S": "J27", "W": None, "dropoff": "E"},
    "J2": {"N": "J3", "E": "D2", "S": "J1", "W": None, "dropoff": "E"},
    "J3": {"N": "J4", "E": "D3", "S": "J2", "W": None, "dropoff": "E"},
    "J4": {"N": "J5", "E": "D4", "S": "J3", "W": None, "dropoff": "E"},
    "J5": {"N": "J6", "E": "D5", "S": "J4", "W": None, "dropoff": "E"},
    "J6": {"N": "J36", "E": "D6", "S": "J5", "W": None, "dropoff": "E"},
    "J7": {"N": "J8", "E": None, "S": "J31", "W": "D7", "dropoff": "W"},
    "J8": {"N": "J9", "E": None, "S": "J7", "W": "D8", "dropoff": "W"},
    "J9": {"N": "J10", "E": None, "S": "J8", "W": "D9", "dropoff": "W"},
    "J10": {"N": "J11", "E": None, "S": "J9", "W": "D10", "dropoff": "W"},
    "J11": {"N": "J12", "E": None, "S": "J10", "W": "D11", "dropoff": "W"},
    "J12": {"N": "J37", "E": None, "S": "J11", "W": "D12", "dropoff": "W"},
    "J13": {"N": "J14", "E": None, "S": "J34", "W": "D13", "dropoff": "W"},
    "J14": {"N": "J15", "E": None, "S": "J13", "W": "D14", "dropoff": "W"},
    "J15": {"N": "J16", "E": None, "S": "J14", "W": "D15", "dropoff": "W"},
    "J16": {"N": "J17", "E": None, "S": "J15", "W": "D16", "dropoff": "W"},
    "J17": {"N": "J18", "E": None, "S": "J16", "W": "D17", "dropoff": "W"},
    "J18": {"N": None, "E": None, "S": "J17", "W": "D18", "dropoff": "W"},
    "J19": {"N": "J20", "E": "D19", "S": "J35", "W": None, "dropoff": "E"},
    "J20": {"N": "J21", "E": "D20", "S": "J19", "W": None, "dropoff": "E"},
    "J21": {"N": "J22", "E": "D21", "S": "J20", "W": None, "dropoff": "E"},
    "J22": {"N": "J23", "E": "D22", "S": "J21", "W": None, "dropoff": "E"},
    "J23": {"N": "J24", "E": "D23", "S": "J22", "W": None, "dropoff": "E"},
    "J24": {"N": None, "E": "D24", "S": "J23", "W": None, "dropoff": "E"},
    "J25": {"N": None, "E": "J33", "S": "J26", "W": "J32"},
    "J26": {"N": "J25", "E": "J35", "S": None, "W": "J34"},
    "J27": {"N": "J1", "E": "J28", "S": "P1", "W": None},
    "J28": {"N": None, "E": "J29", "S": "P2", "W": "J27"},
    "J29": {"N": None, "E": "J30", "S": "S", "W": "J28"},
    "J30": {"N": None, "E": "J31", "S": "P3", "W": "J29"},
    "J31": {"N": "J7", "E": None, "S": "P4", "W": "J30"},
    "J32": {"N": None, "E": "J25", "S": "J36", "W": None},
    "J33": {"N": None, "E": None, "S": "J37", "W": "J25"},
    "J34": {"N": "J13", "E": "J26", "S": None, "W": None},
    "J35": {"N": "J19", "E": None, "S": None, "W": "J26"},
    "J36": {"N": "J32", "E": None, "S": "J6", "W": None},
    "J37": {"N": "J33", "E": None, "S": "J12", "W": None},
    # Pickups
    "P1": {"N": "J27", "E": None, "S": None, "W": None},
    "P2": {"N": "J28", "E": None, "S": None, "W": None},
    "P3": {"N": "J30", "E": None, "S": None, "W": None},
    "P4": {"N": "J31", "E": None, "S": None, "W": None},
    # Dropoffs D1–D24
    "D1": {"N": None, "E": None, "S": None, "W": "J1"},
    "D2": {"N": None, "E": None, "S": None, "W": "J2"},
    "D3": {"N": None, "E": None, "S": None, "W": "J3"},
    "D4": {"N": None, "E": None, "S": None, "W": "J4"},
    "D5": {"N": None, "E": None, "S": None, "W": "J5"},
    "D6": {"N": None, "E": None, "S": None, "W": "J6"},
    "D7": {"N": None, "E": "J7", "S": None, "W": None},
    "D8": {"N": None, "E": "J8", "S": None, "W": None},
    "D9": {"N": None, "E": "J9", "S": None, "W": None},
    "D10": {"N": None, "E": "J10", "S": None, "W": None},
    "D11": {"N": None, "E": "J11", "S": None, "W": None},
    "D12": {"N": None, "E": "J12", "S": None, "W": None},
    "D13": {"N": None, "E": "J13", "S": None, "W": None},
    "D14": {"N": None, "E": "J14", "S": None, "W": None},
    "D15": {"N": None, "E": "J15", "S": None, "W": None},
    "D16": {"N": None, "E": "J16", "S": None, "W": None},
    "D17": {"N": None, "E": "J17", "S": None, "W": None},
    "D18": {"N": None, "E": "J18", "S": None, "W": None},
    "D19": {"N": None, "E": None, "S": None, "W": "J19"},
    "D20": {"N": None, "E": None, "S": None, "W": "J20"},
    "D21": {"N": None, "E": None, "S": None, "W": "J21"},
    "D22": {"N": None, "E": None, "S": None, "W": "J22"},
    "D23": {"N": None, "E": None, "S": None, "W": "J23"},
    "D24": {"N": None, "E": None, "S": None, "W": "J24"},
}
