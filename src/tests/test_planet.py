#!/usr/bin/env python3

import unittest
from planet_new import Direction, Planet


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 0), Direction.WEST), ((0, 1), Direction.WEST), 2)
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet.add_path(((0, 1), Direction.NORTH), ((0, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.NORTH), ((0, 3), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.EAST), ((2, 2), Direction.WEST), 2)
        self.planet.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 2)
        self.planet.add_path(((0, 3), Direction.EAST), ((2, 2), Direction.NORTH), 3)
        self.planet.add_path(((1, 0), Direction.NORTH), ((2, 2), Direction.SOUTH), 3)

    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNotNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        self.planet = Planet()
        self.planet.add_path(((3, 4), Direction.WEST), ((3, 4), Direction.WEST), 0)
        self.planet.add_path(((3, 4), Direction.WEST), ((2, 4), Direction.EAST), 1)
        self.planet.add_path(((2, 4), Direction.WEST), ((1, 5), Direction.SOUTH), 1)
        self.planet.add_path(((1, 5), Direction.EAST), ((3, 5), Direction.WEST), 1)
        self.planet.add_path(((3, 5), Direction.EAST), ((3, 7), Direction.EAST), 3)
        self.planet.add_path(((3, 7), Direction.NORTH), ((2, 8), Direction.EAST), 4)
        self.planet.add_path(((2, 8), Direction.WEST), ((1, 6), Direction.NORTH), 2)
        self.planet.add_path(((1, 6), Direction.EAST), ((2, 6), Direction.WEST), 2)
        self.planet.add_path(((2, 6), Direction.NORTH), ((2, 8), Direction.SOUTH), 5)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure

        assume

        action

        assert
        """
        self.assertIs(type(self.planet.get_paths()), dict)
        self.assertIs(type(list(self.planet.get_paths().keys())[0]), tuple)
        self.assertIs(type(list(self.planet.get_paths().values())[0]), dict)
        self.assertIs(type(list(list(self.planet.get_paths().values())[0].keys())[0]), Direction)
        self.assertIs(type(list(list(self.planet.get_paths().values())[0].values())[0]), tuple)

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty

        assume

        action

        assert"""

        self.planet = Planet()
        self.assertFalse(self.planet.get_paths())

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.
        Requirement: Minimum distance is three nodes (two paths in list returned)
        """

        self.assertEqual(self.planet.shortest_path((3, 4), (3, 7)), [((3, 4), Direction.WEST),
                                                                     ((2, 4), Direction.WEST),
                                                                     ((1, 5), Direction.EAST),
                                                                     ((3, 5), Direction.EAST)])

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        # Obstacle on the way
        self.assertIsNotNone(self.planet.shortest_path((3, 4), (2, 6)), [((3, 4), Direction.WEST),
                                                                         ((2, 4), Direction.WEST),
                                                                         ((1, 5), Direction.EAST),
                                                                         ((3, 5), Direction.EAST),
                                                                         ((3, 7), Direction.SOUTH)])
        # target not on map
        self.assertIsNone(self.planet.shortest_path((3, 4), (1, 4)), [((3, 4), Direction.WEST),
                                                                      ((2, 4), Direction.WEST),
                                                                      ((1, 5), Direction.EAST)])

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        a = [((2, 6), Direction.WEST)]
        b = [((2, 6), Direction.EAST)]
        c = self.planet.shortest_path((2, 6), (1, 6))
        self.assertTrue(a == c or b == c)

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        self.assertEqual(self.planet.shortest_path((3, 4), (3, 7)), [((3, 4), Direction.WEST),
                                                                     ((2, 4), Direction.WEST),
                                                                     ((1, 5), Direction.EAST),
                                                                     ((3, 5), Direction.EAST)])

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        # adding a loop near unreachable
        self.planet.add_path(((1, 5), Direction.EAST), ((3, 5), Direction.WEST), 1)
        self.assertIsNotNone(self.planet.shortest_path((3, 4), (3, 7)))


if __name__ == "__main__":
    unittest.main()
