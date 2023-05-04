#!/usr/bin/env python3

# This file was provided by a tutor

from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union
from time import sleep
import math


# IMPORTANT NOTE: DO NOT IMPORT THE ev3dev.ev3 MODULE IN THIS FILE

@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


# simple alias, no magic here
Weight = int
""" 
    Weight of a given path (received from the server)
    value:  -1 if blocked path
            >0 for all other paths
            never 0
"""


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure """
        self.target = None
        self.name = ""
        self.path_dict: Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]] = {}
        self.backtrack_target = None
        self.backtrack_target_queue = list()
        self.current_node = (0, 0)
        self.path_queue = list()
        self.planet_map = {}
        self.com = None
        self.target_unreachable = False
        self.visited_nodes = list()
        self.node_queue = list()

    def set_name(self, name):
        self.name = name

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
        Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """
        for point1, point2 in [(start, target), (target, start)]:
            if point1[0] not in self.path_dict.keys():
                value = {point1[1]: (point2[0], point2[1], weight)}
                self.path_dict[point1[0]] = value
            else:
                self.path_dict[point1[0]][point1[1]] = (point2[0], point2[1], weight)

    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """
        return self.path_dict

    def get_data(self, xs, ys, directions):
        self.planet_map = self.get_paths()              # get dict with paths
        self.current_node = (xs, ys)                    # set current_node
        self.visited_nodes.append(self.current_node)    # add current_node to visited nodes
        if self.current_node in self.node_queue:        # if the current node is already in node queue don't append it
            self.node_queue.remove(self.current_node)

        for i in range(len(directions)):                # check for every direction
            if self.current_node in self.planet_map:    # if node is already in map
                if directions[i] not in self.planet_map[self.current_node]:  # if direction of paths from node in map
                    if (self.current_node, directions[i]) not in self.path_queue:   # and if outgoing path not in queue
                        self.path_queue.append((self.current_node, directions[i]))  # then add to queue
            else:
                if (self.current_node, directions[i]) not in self.path_queue:       # if path not already in queue
                    self.path_queue.append((self.current_node, directions[i]))      # then add to queue

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: 2-Tuple[List, Direction]
        """

        if start not in self.get_paths().keys() or target not in self.get_paths().keys():
            return None

        if start == target:
            return []

        unvisited_nodes = set(self.get_paths().keys())
        table: Dict[Tuple[int, int], Tuple[int, Tuple[int, int], Direction]] = {start: (0, (0, 0), Direction.NORTH)}

        last_node = target

        while unvisited_nodes:

            current_node = target
            current_dist = math.inf

            for node in table:
                if node in unvisited_nodes and table.get(node)[0] < current_dist:
                    current_node = node
                    current_dist = table.get(node)[0]

            if current_node == last_node:
                break

            for direction in self.get_paths().get(current_node).keys():
                node = self.get_paths().get(current_node).get(direction)[0]
                weight = self.get_paths().get(current_node).get(direction)[2]
                if (node not in table.keys() or current_dist + weight < table.get(node)[0]) and weight != -1:
                    table[node] = (current_dist + weight, current_node, direction)

            unvisited_nodes.remove(current_node)

        path: List[Tuple[Tuple[int, int], Direction]] = []
        node = target

        if node not in table:
            return None

        while node != start:
            direction = table.get(node)[2]
            node = table.get(node)[1]
            path.insert(0, (node, direction))

        return path

    def find_valid_node(self):          # searches through node queue to find reachable nodes
        helper_node_queue = list()
        helper_node_queue = self.node_queue
        if not helper_node_queue == []:
            for i in range(len(helper_node_queue)):
                if self.shortest_path(self.current_node, helper_node_queue[-i]) is not None:
                    return helper_node_queue[-i]
        return None

    def find_valid_backtrack(self):     # searches through backtrack points to find reachable ones
        helper_backtrack_queue = list()
        helper_backtrack_queue = self.backtrack_target_queue
        if not helper_backtrack_queue == []:
            for i in range(len(helper_backtrack_queue)):
                if self.shortest_path(self.current_node, helper_backtrack_queue[-i]) is not None:
                    return helper_backtrack_queue[-i]
        return None

    def check_target(self):
        if self.current_node == self.target:    # check if target reached
            self.target = None                  # if true reset target
            self.com.target_reached_message()   # send target reached
            sleep(3)

        if self.target is not None:  # check if target set
            selected = self.shortest_path(self.current_node, self.target)   # generate shortest path to target
            if selected is None:                                            # if target not reachable
                print("Target unreachable")
                self.target_unreachable = True
                return self.depth_first_search()    # continue with dfs and keep target
            else:
                self.target_unreachable = False     # if target reachable drive to target
                selected_direction = selected[0][1]
                return selected_direction           # return next direction to target
        else:
            return self.depth_first_search()        # if no target set continue dfs

    def clean_up_queue(self):
        i = 0
        while i < len(self.path_queue):             # remove unnecessary paths from queue
            if self.path_queue[i][0] in self.planet_map:
                if self.path_queue[i][1] in self.planet_map[self.path_queue[i][0]]:
                    self.path_queue.pop(i)
                    continue
            i = i + 1

        print("DEBUG: PATH_QUEUE: ", self.path_queue)

    def clean_up_node_queue(self):                  # remove nodes of which all four paths are known
        for node in self.node_queue:
            if node in self.planet_map:
                if len(self.planet_map[node]) == 4:
                    self.node_queue.remove(node)

        print("DEBUG: NODE_QUEUE", self.node_queue)

    def depth_first_search(self):
        self.clean_up_queue()
        self.clean_up_node_queue()

        print("DEBUG: BACKTRACK QUEUE", self.backtrack_target_queue)

        if self.current_node == self.backtrack_target:              # check if backtrack target reached
            self.backtrack_target_queue.remove(self.current_node)
            self.backtrack_target = None

        if self.backtrack_target is not None:                                        # if backtrack target is set
            selected = self.shortest_path(self.current_node, self.backtrack_target)  # generate shortest path to target
            return selected[0][1]

        else:
            if not self.path_queue:                 # if path queue is empty
                if not self.node_queue == []:       # if queue empty but node queue not empty
                    valid = self.find_valid_node()  # find valid nodes
                    if valid is None:               # if no valid nodes exist return
                        print("Complete")
                        return "exploration completed"
                    else:
                        selected = self.shortest_path(self.current_node, valid)  # if valid node exists, pathfind
                        return selected[0][1]

                else:                               # if queue and node queue empty exploration finished
                    print("Complete")
                    return "exploration completed"
            else:
                if self.current_node not in list(
                        dict(self.path_queue).keys()):          # if current node has no paths in queue left
                    target_tuple = self.path_queue[-1][0]       # get last node from path queue
                    self.backtrack_target_queue.append(target_tuple)  # append last node to backtrack queue
                    backtrack = self.find_valid_backtrack()     # get valid backtrack
                    if backtrack is None:                       # if no valid backtrack left, exploration finished
                        self.com.exploration_completed_message()
                        return "exploration completed"
                    self.backtrack_target = backtrack                                        # set backtrack target
                    selected = self.shortest_path(self.current_node, self.backtrack_target)  # generate shortest path
                    selected_direction = selected[0][1]                                      # get direction to drive
                    return selected_direction

                else:                               # if current node has paths in queue
                    selected = self.path_queue[-1]  # remove path from queue and follow it
                    selected_direction = selected[1]
                    return selected_direction
