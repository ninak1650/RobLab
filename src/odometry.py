import ev3dev.ev3 as ev3
import math

motor_left = ev3.LargeMotor("outA")
motor_right = ev3.LargeMotor("outB")


class Odometry:
    def __init__(self, com):
        self.wheel_radius = 28  # ALL measurements and distances in mm
        self.distance_wheels = 130
        self.millimeter_per_tick = 0.47
        self.motor_pos_l = list()
        self.motor_pos_r = list()
        self.total_pos_l = list()
        self.total_pos_r = list()
        self.x_coord = 0
        self.y_coord = 0
        self.x_delta = list()
        self.y_delta = list()
        self.x_delta_total = 0
        self.y_delta_total = 0
        self.alpha = list()
        self.alpha_total = 0
        self.radius = list()
        self.distance_l = list()
        self.distance_r = list()
        self.distance_driven = list()
        self.distance_driven_total = 0
        self.calculated_alignment = 0
        self.com = com
        self.entrance_alignment = 0
        self.exit_alignment = 0

    def get_data(self):                                 # get coordinates from com and multiply them by 500 (mm)
        self.x_coord = self.com.Xs * 500
        self.y_coord = self.com.Ys * 500
        # print("DEBUG: X_START =", self.x_coord, "Y_START =", self.y_coord, "DIRECTION_START =",
              # self.calculated_alignment)

    def get_motor_pos(self):                            # log motor position in intervals (called while driving)
        self.motor_pos_l.append(motor_left.position)
        self.motor_pos_r.append(motor_right.position)
        # print("DEBUG: NEW_POS_L =", self.motor_pos_l, "NEW_POS_R =", self.motor_pos_r)

    def calc_total_pos(self):                           # calculate delta of motor positions between intervals
        helper = 1
        length = len(self.motor_pos_l)
        for i in range(length):
            if length - 1 == i:
                helper = 0
            self.total_pos_l.append(self.motor_pos_l[i + helper] - self.motor_pos_l[i])
            self.total_pos_r.append(self.motor_pos_r[i + helper] - self.motor_pos_r[i])
        motor_left.reset()
        motor_right.reset()
        # print("DEBUG: TOTAL_POS_L =", self.total_pos_l, "TOTAL_POS_R =", self.total_pos_r)

    def calc_distance_per_wheel(self):                  # calculate distance driven per interval
        length = len(self.total_pos_l)
        for i in range(length):
            self.distance_l.append(self.total_pos_l[i] * self.millimeter_per_tick)
            self.distance_r.append(self.total_pos_r[i] * self.millimeter_per_tick)
        # print("DEBUG: DISTANCE_L =", self.distance_l, "DISTANCE_R", self.distance_r)

    def calc_alpha(self):                               # calculate alpha per interval
        length = len(self.distance_l)
        for i in range(length):
            if self.distance_l[i] == self.distance_r[i]:
                self.alpha.append(0.0000000001)        # if alpha == 0 set alpha to small value to prevent zero division
            else:
                self.alpha.append((self.distance_r[i] - self.distance_l[i]) / self.distance_wheels)

    def calc_distance_driven(self):                     # calculate driven distance per interval
        length = len(self.alpha)
        for i in range(length):
            self.distance_driven.append(
                ((self.distance_l[i] + self.distance_r[i]) / self.alpha[i]) * math.sin(self.alpha[i] / 2))
        self.distance_driven_total = sum(self.distance_driven)

    def calc_xy(self):                                  # calculate x and y coordinates
        length = len(self.alpha)
        for i in range(length):
            self.x_delta.append(- math.sin(- self.calculated_alignment + (self.alpha[i] / 2)) * self.distance_driven[i])
            self.y_delta.append(math.cos(- self.calculated_alignment + (self.alpha[i] / 2)) * self.distance_driven[i])
            self.calculated_alignment = self.calculated_alignment - self.alpha[i]
            if self.calculated_alignment == 360:
                self.calculated_alignment = 0

        self.x_delta_total = sum(self.x_delta)          # calculate x delta and x coord
        self.x_coord = self.x_coord + self.x_delta_total
        # print("DEBUG: DELTA_X =", self.x_delta_total, "X =", self.x_coord, "mm")

        self.y_delta_total = sum(self.y_delta)          # calculate y delta and y coord
        self.y_coord = self.y_coord + self.y_delta_total
        # print("DEBUG: DELTA_Y =", self.y_delta_total, "Y =", self.y_coord, "mm")

        # print("DEBUG: ALIGNMENT =", self.calculated_alignment)

    def round(self):                                    # round x, y and alignment
        self.calculated_alignment = round((math.degrees(self.calculated_alignment) % 360) / 90) * 90
        if self.calculated_alignment == 360:
            self.calculated_alignment = 0
        self.entrance_alignment = round(((self.calculated_alignment + 180) % 360) / 90) * 90
        if self.entrance_alignment == 360:
            self.entrance_alignment = 0
        self.x_coord = round(self.x_coord / 500)
        self.y_coord = round(self.y_coord / 500)
        # print("ROUNDED_ALIGNMENT =", self.calculated_alignment, "ENTRANCE_ALIGNMENT =", self.entrance_alignment,
        #      "ROUNDED_X =", self.x_coord, "ROUNDED_Y =", self.y_coord)

    def odo_starter(self):      # starts odometry
        self.get_data()
        self.calc_total_pos()
        self.calc_distance_per_wheel()
        self.calc_alpha()
        self.calc_distance_driven()
        self.calc_xy()
        self.round()
        # print("DEBUG: DISTANCE_DRIVEN_TOTAL =", self.distance_driven_total, "mm")
        return self.x_coord, self.y_coord, self.entrance_alignment

    def reset(self):            # resets odometry
        self.motor_pos_l = []
        self.motor_pos_r = []
        self.total_pos_l = []
        self.total_pos_r = []
        self.x_delta = []
        self.y_delta = []
        self.x_delta_total = 0
        self.y_delta_total = 0
        self.alpha = []
        self.alpha_total = 0
        self.radius = []
        self.distance_l = []
        self.distance_r = []
        self.distance_driven = []
        self.distance_driven_total = 0

    def calc_path_direction(self, bool_tupel):      # takes boolean tuple generated by path scan and converts it into
        direction_list = list()                     # directions
        if bool_tupel[0]:
            direction_list.append(self.calculated_alignment)
        if bool_tupel[1] == True:
            if self.calculated_alignment - 90 < 0:
                direction_list.append(270)
            else:
                direction_list.append(self.calculated_alignment - 90)
        if bool_tupel[2] == True:
            if self.calculated_alignment + 90 == 360:
                direction_list.append(0)
            else:
                direction_list.append(self.calculated_alignment + 90)
        return direction_list

    def calc_move_selector(self, exit_alignment):   # uses current direction / alignment and target to calculate needed
        self.exit_alignment = exit_alignment        # move
        alignment_delta = exit_alignment - self.calculated_alignment
        move_selector = (alignment_delta % 360) / 90
        # print("MOVE_SELECTOR =", move_selector)
        return move_selector
