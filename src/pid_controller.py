import ev3dev.ev3 as ev3

colorsensor = ev3.ColorSensor()
colorsensor.mode = "RGB-RAW"
screen = ev3.Screen()
button = ev3.Button()


class PID_Controller:
    def __init__(self, calibrated_white, calibrated_black):
        self.upper_boundary = calibrated_white
        self.lower_boundary = calibrated_black
        self.target = 0
        self.actual_value = 0
        self.error = 0
        self.last_error = 0
        self.factor = 1
        self.voltage_factor = 1
        self.prop = 0
        self.integ = 0
        self.deriv = 0
        self.kp = 0.1  # Kc=0.15
        self.ki = 0.016
        self.kd = 0.04
        self.dt = 1
        self.target_speed = 0
        self.correction = 0

    def calc_target(self):      # calculate target value
        self.target = (self.upper_boundary + self.lower_boundary) / 2
        # print("DEBUG: TARGET = ", self.target)

    def calc_error(self):       # calculate error (offset from target value)
        self.calc_target()
        self.actual_value = sum(colorsensor.bin_data("hhh"))
        # print("DEBUG: ACTUAL VALUE =", self.actual_value)
        self.error = self.actual_value - self.target
        # print("DEBUG: ERROR =", self.error)

    def calc_factor(self):      # calculate cubic multiplier
        self.factor = 1 + (0.000933333 * abs(self.error) + ((2.77778 * (10 ** -6)) * (abs(self.error ** 2))))

    def calc_battery_voltage_factor(self):  # calculate correction factor for battery voltage
        with open('/sys/class/power_supply/lego-ev3-battery/voltage_now') as voltage_file:
            voltage = int(voltage_file.read()) * (10 ** (-6))
            self.voltage_factor = 0.02 * voltage + 0.82
            # print("DEBUG: VOLTAGE =", voltage)

    def calc_target_speed(self):    # calculate target speed (adaptive)
        self.calc_battery_voltage_factor()
        self.target_speed = (200 - (0.0169901 * self.correction) - (0.0027134 * (self.correction ** 2)) + (
                    3.737 * (10 ** (-6)) * (self.correction ** 3))) * self.voltage_factor

    def calc_proportional(self):    # calculate proportional part of pid
        self.calc_error()
        self.calc_factor()
        self.prop = self.kp * self.error
        # print("DEBUG: PROPORTIONAL =", self.prop)

    def calc_integral(self):        # calculate integral part of pid
        self.integ = self.ki * (self.integ + (self.error * self.dt))
        # print("DEBUG: INTEGRAL =", self.integ)

    def calc_derivative(self):      # calculate derivative part of pid
        self.deriv = (self.kd * (self.prop - self.last_error) / self.dt)
        # print("DEBUG: DERIVATIVE =", self.deriv)

    def calc_correction(self):      # call methods and calculate needed correction
        self.calc_proportional()
        self.calc_integral()
        self.calc_derivative()
        self.correction = (self.prop + self.integ + self.deriv) * self.factor
        # print("DEBUG: CORRECTION =", self.correction)

    def follow_line(self):          # call methods and calculate motor speed
        self.calc_correction()
        self.calc_target_speed()
        motor_right_speed = self.target_speed + self.correction
        motor_left_speed = self.target_speed - self.correction
        self.last_error = self.error
        return motor_right_speed, motor_left_speed
