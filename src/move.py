import ev3dev.ev3 as ev3
from pid_controller import PID_Controller
from time import sleep
import time

motor_left = ev3.LargeMotor("outA")
motor_right = ev3.LargeMotor("outB")
colorsensor = ev3.ColorSensor()
colorsensor.mode = "RGB-RAW"


class Movement:
    def __init__(self, black, white, odo):
        self.calibrated_black = black
        self.calibrated_white = white
        self.target = ((self.calibrated_white + self.calibrated_black) / 2) - 100
        self.motor_pos_l = 0
        self.motor_pos_r = 0
        self.odo = odo

    def move_along_line(self):      # follow line by using the pid controller
        # print("DEBUG: FOLLOW_LINE")
        pid = PID_Controller(self.calibrated_white, self.calibrated_black)
        correction_tupel = pid.follow_line()
        motor_left.speed_sp = correction_tupel[0]
        motor_right.speed_sp = correction_tupel[1]

        motor_left.command = "run-forever"
        motor_right.command = "run-forever"

    def forwards(self):             # drive forwards slowly
        motor_left.speed_sp = 100
        motor_right.speed_sp = 100
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(1.6)
        self.motor_stop()

    def backwards(self):            # drive backwards slowly
        motor_left.speed_sp = - 100
        motor_right.speed_sp = - 100
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(2.2)
        self.motor_stop()

    def rotate_left(self):          # rotate to the next line on the left
        motor_left.speed_sp = - 100
        motor_right.speed_sp = 100
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(1.2)

        while sum(colorsensor.bin_data("hhh")) > self.target:
            motor_left.speed_sp = - 100
            motor_right.speed_sp = 100
            motor_left.command = "run-forever"
            motor_right.command = "run-forever"

        self.stop_and_reset()

    def rotate_right(self):         # rotate to the next line on the right
        motor_left.speed_sp = 100
        motor_right.speed_sp = - 100
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(1)

        while sum(colorsensor.bin_data("hhh")) > self.target:
            motor_left.speed_sp = 100
            motor_right.speed_sp = - 100
            motor_left.command = "run-forever"
            motor_right.command = "run-forever"

        self.stop_and_reset()

    def search_left(self):          # scan for paths to the left
        path_left = False

        motor_left.speed_sp = - 200
        motor_right.speed_sp = 200
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(0.4)

        timeout = time.time() + 0.8

        while time.time() < timeout:
            motor_left.speed_sp = - 200
            motor_right.speed_sp = 200
            motor_left.command = "run-forever"
            motor_right.command = "run-forever"

            if sum(colorsensor.bin_data("hhh")) < self.target:
                path_left = True
                # print("DEBUG: PATH_LEFT DETECTED")

        self.motor_stop()

        motor_left.speed_sp = 200
        motor_right.speed_sp = - 200
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(1.2)

        self.stop_and_reset()
        return path_left

    def search_right(self):         # scan for paths to the right
        path_right = False

        motor_left.speed_sp = 200
        motor_right.speed_sp = - 200
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(0.4)

        timeout = time.time() + 0.8

        while time.time() < timeout:
            motor_left.speed_sp = 200
            motor_right.speed_sp = - 200
            motor_left.command = "run-forever"
            motor_right.command = "run-forever"

            if sum(colorsensor.bin_data("hhh")) < self.target:
                path_right = True
                # print("DEBUG: PATH_RIGHT DETECTED")

        self.motor_stop()

        motor_left.speed_sp = - 200
        motor_right.speed_sp = 200
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(1.2)

        self.stop_and_reset()
        return path_right

    def search_straight(self):      # scan for paths in front of rover
        path_straight = False
        self.forwards()
        if sum(colorsensor.bin_data("hhh")) < self.target:
            path_straight = True
            # print("DEBUG: PATH_STRAIGHT DETECTED")
        else:
            motor_right.speed_sp = 200
            motor_right.command = "run-forever"
            timeout = time.time() + 0.55
            while time.time() < timeout:
                if sum(colorsensor.bin_data("hhh")) < self.target:
                    path_straight = True
                    # print("DEBUG: PATH_STRAIGHT DETECTED")
            motor_right.stop()

            motor_right.speed_sp = - 200
            motor_right.command = "run-forever"
            sleep(0.55)
            motor_right.stop()

            motor_left.speed_sp = 200
            motor_left.command = "run-forever"
            timeout = time.time() + 0.55
            while time.time() < timeout:
                if sum(colorsensor.bin_data("hhh")) < self.target:
                    path_straight = True
                    # print("DEBUG: PATH_STRAIGHT DETECTED")
            motor_left.stop()

            motor_left.speed_sp = - 200
            motor_left.command = "run-forever"
            sleep(0.55)
            motor_left.stop()

        self.motor_reset()
        return path_straight

    def turn_around(self):      # turn around
        motor_left.speed_sp = 100
        motor_right.speed_sp = - 100
        motor_left.command = "run-forever"
        motor_right.command = "run-forever"
        sleep(3)

        while sum(colorsensor.bin_data("hhh")) > self.target:
            motor_left.speed_sp = 100
            motor_right.speed_sp = - 100
            motor_left.command = "run-forever"
            motor_right.command = "run-forever"

        self.motor_stop()

    def path_blocked(self):     # if path blocked drive backwards and turn around
        self.backwards()
        self.turn_around()

    def movement_selector(self, move_number):   # call movement method
        if move_number == 0:
            pass
        elif move_number == 1:
            self.rotate_right()
        elif move_number == 2:
            self.turn_around()
        elif move_number == 3:
            self.rotate_left()

    @staticmethod
    def motor_stop():
        motor_right.stop()
        motor_left.stop()

    @staticmethod
    def motor_reset():
        motor_left.reset()
        motor_right.reset()

    @staticmethod
    def stop_and_reset():
        motor_right.stop()
        motor_right.reset()
        motor_left.stop()
        motor_left.reset()
