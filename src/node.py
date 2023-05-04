import ev3dev.ev3 as ev3
from move import Movement

colorsensor = ev3.ColorSensor()
colorsensor.mode = "RGB-RAW"
motor_left = ev3.LargeMotor("outA")
motor_right = ev3.LargeMotor("outB")


class Node:
    def __init__(self, red_value_list, blue_value_list, black, white, odo):
        self.red_red_threshold = red_value_list[0] - 50         # set thresholds for red node detection
        self.red_green_threshold = red_value_list[1] + 20
        self.red_blue_threshold = red_value_list[2] + 20

        self.blue_red_threshold = blue_value_list[0] + 20       # set thresholds for blue node detection
        self.blue_green_threshold = blue_value_list[1] + 20
        self.blue_blue_threshold = blue_value_list[2] - 50

        self.actual_red = 0
        self.actual_green = 0
        self.actual_blue = 0

        self.calibrated_black = black   # black value found by calibration
        self.calibrated_white = white   # white value found by calibration

        self.odo = odo

        self.left = False               # path variables
        self.right = False
        self.straight = False

    def check_for_node(self):           # node detection
        self.actual_red = colorsensor.value(0)
        self.actual_green = colorsensor.value(1)
        self.actual_blue = colorsensor.value(2)

        # print("DEBUG: RED VALUE =", self.actual_red, "THRESHOLD RED =", self.red_red_threshold, "THRESHOLD BLUE =",
        #      self.red_blue_threshold)
        # print("DEBUG: GREEN VALUE =", self.actual_green, "THRESHOLD RED =", self.red_green_threshold,
        #      "THRESHOLD BLUE =", self.blue_green_threshold)
        # print("DEBUG: BLUE VALUE =", self.actual_blue, "THRESHOLD RED =", self.red_blue_threshold, "THRESHOLD BLUE =",
        #      self.blue_blue_threshold)

        if self.red_red_threshold < self.actual_red and self.red_green_threshold > self.actual_green \
                and self.red_blue_threshold > self.actual_blue:
            #    print("DEBUG: RED NODE TRUE")
            return True
        elif self.blue_red_threshold > self.actual_red and self.blue_green_threshold > self.actual_green \
                and self.blue_blue_threshold < self.actual_blue:
            #    print("DEBUG: BLUE NODE TRUE")
            return True
        else:
            #    print("DEBUG: NO NODE")
            return False

    def node_detected(self):    # if node detected scan for paths
        move = Movement(self.calibrated_black, self.calibrated_white, self.odo)
        self.straight = move.search_straight()
        self.left = move.search_left()
        self.right = move.search_right()
        move.motor_reset()
        print("DEBUG: PATHS_DETECTED: ", self.straight, self.left, self.right)
        return self.straight, self.left, self.right

    def reset(self):            # reset discovered paths
        self.straight = False
        self.left = False
        self.right = False
