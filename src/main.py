#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging
import os
import paho.mqtt.client as mqtt
import uuid
import signal
import math

from communication import Communication
from odometry import Odometry
from planet import Direction, Planet
from node import Node
from calibration import Calibration
from move import Movement
from time import sleep

client = None  # DO NOT EDIT


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client_id = '112-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
    client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                         clean_session=True,  # We want a clean session after disconnect or abort/crash
                         protocol=mqtt.MQTTv311  # Define MQTT protocol version
                         )
    log_file = os.path.realpath(__file__) + '/../../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    # Unlock motors

    motor_left = ev3.LargeMotor("outA")
    motor_right = ev3.LargeMotor("outB")
    motor_left.reset()
    motor_right.reset()
    motor_left.stop_action = "brake"
    motor_right.stop_action = "brake"

    # Define ultrasonic sensor

    ultrasensor = ev3.UltrasonicSensor()
    ultrasensor.mode = "US-DIST-CM"

    # Calibrate and get data

    calib = Calibration()
    calib.start_calibration()
    black = calib.calibrated_black
    white = calib.calibrated_white
    red = calib.calibrated_red
    blue = calib.calibrated_blue

    # define needed modules

    com = Communication(client, logger)
    odo = Odometry(com)
    move = Movement(black, white, odo)
    node = Node(red, blue, black, white, odo)
    planet = Planet()
    com.link_to_planet = planet

    # set start parameters, choose testplanet

    is_landing = True
    # com.testplanet()
    obstacle = "free"
    planet.com = com
    scanned_nodes = list()

    while True:

        # follow line and log motor positions

        if not node.check_for_node():

            move.move_along_line()
            odo.get_motor_pos()

            # obstacle detection

            if ultrasensor.distance_centimeters < 8:    # if obstacle detected
                print("DEBUG: OBSTACLE")
                obstacle = "blocked"
                move.motor_stop()
                ev3.Sound.speak("Obstacle detected!")
                move.turn_around()

        # on node detection
        else:
            move.motor_stop()
            if is_landing:                                  # if first node
                is_landing = False
                com.landing_message()                       # send ready
                sleep(3)
                ev3.Sound.beep()
                odo.get_data()                              # get correct x and y coordinate
                odo.calculated_alignment = com.Orientation  # get initial alignment

            # actions at every other node

            else:
                odo_tupel = odo.odo_starter()                                   # start odometry
                odo.reset()                                                     # reset odometry data
                com.path_message(com.Xs, com.Ys, com.Ds, odo_tupel, obstacle)   # send path message
                sleep(3)
                ev3.Sound.beep()
                obstacle = "free"                                               # reset path status

            current_node = (com.Xs, com.Ys)
            # print("Current node: ", current_node)
            # print("Scanned nodes: ", scanned_nodes)

            if not any(x[0] == current_node for x in scanned_nodes):    # if current_node not already scanned, scan it
                path_tupel = node.node_detected()                       # check for node and get outgoing paths
                odo.calculated_alignment = com.Orientation              # get correct orientation from mothership
                path_directions = odo.calc_path_direction(path_tupel)   # calculate directions of paths
                scanned_nodes.append((current_node, path_directions))   # add to list so its not scanned again later

            else:                                                       # if node is already scanned
                move.forwards()                                         # move a bit forwards
                odo.calculated_alignment = com.Orientation              # set orientation
                for x in scanned_nodes:
                    if x[0] == current_node:                            # get path data of current node
                        path_directions = x[1]

            # print("DEBUG: PATH_DIRECTIONS =", path_directions)

            planet.get_data(com.Xs, com.Ys, path_directions)            # give data to planet module
            selected_direction = planet.check_target()                  # start exploration strategy

            if selected_direction == "exploration completed" and planet.target is None:         # win conditions
                com.exploration_completed_message()
                sleep(3)
                ev3.Sound.beep()
            elif selected_direction == "exploration completed" and planet.target_unreachable:
                com.exploration_completed_message()
                sleep(3)
                ev3.Sound.beep()

            if com.finished is True:    # if mothership confirms stop exploration
                move.stop_and_reset()
                break
            else:                       # if not backup x and y
                x_backup = com.Xs
                y_backup = com.Ys
                com.selected_path_message(com.Xs, com.Ys, selected_direction)   # send selected path message
                sleep(3)
                ev3.Sound.beep()
                selected_path = (current_node, com.selectedPath)                # generate tuple

                if current_node in planet.planet_map:                           # check if mothership forces turn into
                    if com.Dc in planet.planet_map[current_node]:               # blocked path
                        if not current_node == planet.planet_map[current_node][com.Dc][0]:
                            if planet.planet_map[current_node][com.Dc][2] == -1:            # if it does send fake
                                fake_x = planet.planet_map[current_node][com.Dc][0][0]      # message
                                fake_y = planet.planet_map[current_node][com.Dc][0][1]
                                fake_direction = planet.planet_map[current_node][com.Dc][1]
                                com.path_message(com.Xs, com.Ys, com.Dc, (fake_x, fake_y, fake_direction), "blocked")
                                sleep(3)
                                ev3.Sound.beep()
                                com.Xs = x_backup               # restoring data overwritten by path message
                                com.Ys = y_backup
                                com.Dc = selected_direction
                                com.selectedPath = selected_direction
                                com.selected_path_message(com.Xs, com.Ys, selected_direction)   # send selected path
                                sleep(3)
                                ev3.Sound.beep()
                                selected_path = (current_node, com.selectedPath)                # execute

                if selected_path in planet.path_queue:          # if the path is already queued, it is removed
                    planet.path_queue.remove(selected_path)
                selected_direction = com.selectedPath
                # print("DEBUG: SELECTED_DIRECTION =", selected_direction)

                move.movement_selector(odo.calc_move_selector(selected_direction))  # calculate needed movement and start it
                com.Ds = selected_direction                                  # set outgoing direction in coms
                odo.calculated_alignment = math.radians(selected_direction)  # set odometry direction to selected

                move.motor_reset()  # reset motor data
                node.reset()        # reset node data

# DO NOT EDIT


def signal_handler(sig=None, frame=None, raise_interrupt=True):
    if client and client.is_connected():
        client.disconnect()
    if raise_interrupt:
        raise KeyboardInterrupt()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        run()
        signal_handler(raise_interrupt=False)
    except Exception as e:
        signal_handler(raise_interrupt=False)
        raise e
