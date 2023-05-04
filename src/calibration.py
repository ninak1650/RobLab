import ev3dev.ev3 as ev3
from time import sleep

colorsensor = ev3.ColorSensor()
colorsensor.mode = "RGB-RAW"
screen = ev3.Screen()
button = ev3.Button()


class Calibration:
    def __init__(self):
        self.val_white = list()
        self.val_black = list()
        self.val_red = list()
        self.val_blue = list()
        self.calibrated_white = None
        self.calibrated_black = None
        self.calibrated_red = list()
        self.calibrated_blue = list()

    def get_values_for_calibration(self, color_string):     # get data from colorsensor
        if color_string == "white":
            self.val_white.append(sum(colorsensor.bin_data("hhh")))
            return

        if color_string == "black":
            self.val_black.append(sum(colorsensor.bin_data("hhh")))
            return

        if color_string == "red":
            self.val_red = (colorsensor.bin_data("hhh"))
            return

        if color_string == "blue":
            self.val_blue = (colorsensor.bin_data("hhh"))
            return

    def calibrate(self, color_string):  # calibrate colors
        self.val_white.clear()
        self.val_black.clear()

        while True:
            if button.any():
                break
            else:
                sleep(0.1)

        for i in range(5):
            self.get_values_for_calibration(color_string)

        if color_string == "white":
            return round(sum(self.val_white) / 5)

        if color_string == "black":
            return round(sum(self.val_black) / 5)

        if color_string == "red":
            return self.val_red

        if color_string == "blue":
            return self.val_blue

    def start_calibration(self):            # call calibration
        print("DEBUG: START CALIBRATION")

        print("DEBUG: CALIBRATING WHITE")
        self.calibrated_white = self.calibrate("white")
        sleep(1)

        print("DEBUG: CALIBRATING BLACK")
        self.calibrated_black = self.calibrate("black")
        sleep(1)

        print("DEBUG: CALIBRATING RED")
        self.calibrated_red = self.calibrate("red")
        sleep(1)

        print("DEBUG: CALIBRATING BLUE")
        self.calibrated_blue = self.calibrate("blue")
        sleep(2)

        print("DEBUG: CALIBRATED_WHITE =", self.calibrated_white)
        print("DEBUG: CALIBRATED_BLACK =", self.calibrated_black)
        print("DEBUG: CALIBRATED_RED =", *self.calibrated_red)
        print("DEBUG: CALIBRATED_BLUE =", *self.calibrated_blue)

    def skip_calibration(self):             # skip calibration process and use predefined values
        self.calibrated_white = 1100
        self.calibrated_black = 220
        self.calibrated_red = (190, 52, 21)
        self.calibrated_blue = (47, 189, 140)
