#####################################################################################################
#
# Logic related to pathfinding.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
#####################################################################################################

from navigation.config import NODE_LIST, NODE_MAP
from navigation.components.types.navigation import JunctionOptions
from logger.logger import logger


class pathfinding:
    def __init__(self):
        self.node_map = NODE_MAP
        self.node_list = NODE_LIST

    def path_find(self, start_node: str, end_node: str):
        """
        Find a path from start_node to end_node using BFS on the map graph.
        Returns a dictionary with the list of nodes and directions to move.
        """
        # Validate nodes
        if start_node not in self.node_list or end_node not in self.node_list:
            raise ValueError("start_node or end_node not in node_list")

        # Trivial case
        if start_node == end_node:
            return {"nodes": [start_node], "moves": []}

        # BFS structures (MicroPython friendly queue implementation)
        queue = [start_node]
        head = 0

        visited = {start_node}
        parent = {}
        parent_dir = {}

        while head < len(queue):
            current = queue[head]
            head += 1

            if current == end_node:
                break

            neighbors = self.node_map[current]
            for direction in neighbors:
                if direction == "dropoff":
                    continue
                neighbor = neighbors[direction]
                if neighbor is None or neighbor in visited:
                    continue

                visited.add(neighbor)
                parent[neighbor] = current
                parent_dir[neighbor] = direction
                queue.append(neighbor)

        # If end_node not reached
        if end_node not in parent and start_node != end_node:
            return None

        # Reconstruct path (backwards)
        path_nodes = [end_node]  # start from end node
        path_dirs = []  # list to hold directions taken

        cur = end_node
        while cur != start_node:
            path_dirs.append(
                parent_dir[cur]
            )  # append direction leading to current node
            cur = parent[cur]  # move to parent node
            path_nodes.append(cur)  # add parent node to path

        path_nodes.reverse()  # reverse to get path from start to end
        path_dirs.reverse()  # reverse directions accordingly

        return {
            "nodes": path_nodes,  # e.g. ["S", "J29", "J26", ...]
            "moves": path_dirs,  # e.g. ["N", "N", "E", ...]
        }

    ORI_TO_INT = {"N": 0, "E": 1, "S": 2, "W": 3}

    @staticmethod
    def compute_turn(current_ori, target_ori):
        ci = pathfinding.ORI_TO_INT[current_ori]
        ti = pathfinding.ORI_TO_INT[target_ori]
        diff = (ti - ci) & 3

        if diff == 0:
            return JunctionOptions.GO_STRAIGHT, current_ori
        elif diff == 1:
            return JunctionOptions.GO_RIGHT, target_ori
        elif diff == 2:
            return JunctionOptions.U_TURN, target_ori
        elif diff == 3:
            return JunctionOptions.GO_LEFT, target_ori
        else:
            logger.log("Pathfinding: error in compute_turn")
            return None, None

    def get_directions(
        self,
        start_node: str,
        end_node: str,
        start_orientation: str,
    ):
        """
        Convert a path (absolute moves) into relative JunctionOptions
        given a starting orientation.
        start_orientation: one of {"N", "E", "S", "W"}
        Returns: List[JunctionOptions]
        """
        # Get absolute moves from BFS
        # We start at the start node (junction) so we should path find from next node
        print(start_node, end_node)
        path = self.path_find(start_node, end_node)
        if path is None:
            # Panic?
            return None

        moves = path["moves"]  # e.g. ["N", "E", "S"]
        logger.log("Nav - moves {}", moves)

        # Clockwise orientation order
        junction_commands = []
        current_orientation = start_orientation

        for move in moves[1:]:
            cmd, current_orientation = self.compute_turn(current_orientation, move)
            logger.log("pathfinding - {} {} {}", current_orientation, move, cmd)
            junction_commands.append(cmd)
        # Return the last turn's orientation

        # Pathfinding now assumes you're already at the node AND you're orinetated correctly.
        # This translates to ignoring the first route command because you're already there.
        return (current_orientation, path["nodes"][1:], junction_commands)


if __name__ == "__main__":
    # Simple test for path_find and get_directions as a debug/sanity check
    test_map = pathfinding()

    start_node = "START_BOX"
    end_node = "P2"
    start_orientation = "N"

    path_result = test_map.path_find(start_node, end_node)
    directions = test_map.get_directions(start_node, end_node, start_orientation)

    print("Path from", start_node, "to", end_node)

    if path_result is None:
        print("No path found")
    else:
        print("Nodes:", path_result["nodes"], f"({len(path_result['nodes'])} nodes)")
        print("Moves:", path_result["moves"], f"({len(path_result['moves'])} moves)")

    print("Start orientation:", start_orientation)
    print("Junction directions:", directions)
