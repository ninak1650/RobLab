#!/usr/bin/env python3

# This file was provided by a tutor
# Attention: Do not import the ev3dev.ev3 module in this file
import math
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union


@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
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

    def set_name(self,name):
        self.name=name

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
