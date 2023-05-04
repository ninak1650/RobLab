#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import platform
import ssl
import time

# Fix: SSL certificate problem on macOS
if all(platform.mac_ver()):
    pass


def timeout_for_message():
    # after last message timeout for 3 sec
    time.sleep(3)


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler
        # Add your client setup here
        self.logger = logger
        self.client.username_pw_set("112", password="3etiIuD8c5")
        self.client.connect("mothership.inf.tu-dresden.de", port=8883)
        self.client.subscribe("explorer/112", qos=1)
        self.client.loop_start()
        print("Communication started")
        self.planetName = ""
        self.Xs = 0
        self.Ys = 0
        self.Ds = 0
        self.Xe = 0
        self.Ye = 0
        self.De = 0
        self.Xc = 0
        self.Yc = 0
        self.Dc = 0
        self.pathStatus = ""
        self.pathWeight = int
        self.Xt = 0
        self.Yt = 0
        self.unveiledPath = []
        self.selectedPath = []
        self.target = None
        self.message = None
        self.finished = False
        self.Orientation = None
        self.link_to_planet = None

        self.x_backup = None
        self.y_backup = None
        self.selectedPath_backup = None

    # DO NOT EDIT THE METHOD SIGNATURE

    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))

        if payload["from"] == "server":
            # message with planet name and start coordinates
            if payload["type"] == "planet":
                self.planetName = payload["payload"]["planetName"]
                self.Xs = payload["payload"]["startX"]
                self.Ys = payload["payload"]["startY"]
                self.Orientation = payload["payload"]["startOrientation"]
                client.subscribe("planet/" + str(self.planetName) + "/112", qos=1)

            # new path for client
            elif payload["type"] == "pathUnveiled":
                start = (payload["payload"]["startX"], payload["payload"]["startY"])
                end = (payload["payload"]["endX"], payload["payload"]["endY"])
                startDirection = payload["payload"]["startDirection"]
                endDirection = payload["payload"]["endDirection"]
                weight = payload["payload"]["pathWeight"]

                if start not in self.link_to_planet.visited_nodes:      # if start node not in visited nodes
                    if start not in self.link_to_planet.node_queue:     # and not in node queue
                        self.link_to_planet.node_queue.append(start)    # then add to node queue
                if end not in self.link_to_planet.visited_nodes:        # if end node not in visited nodes
                    if end not in self.link_to_planet.node_queue:       # and not in queue
                        self.link_to_planet.node_queue.append(end)      # then add to queue
                self.link_to_planet.add_path((start, startDirection), (end, endDirection), weight)

            elif payload["type"] == "path":
                self.Xs = payload["payload"]["endX"]
                self.Ys = payload["payload"]["endY"]
                self.Orientation = payload["payload"]["endDirection"]
                self.Orientation = round(((self.Orientation + 180) % 360) / 90) * 90
                if self.Orientation == 360:
                    self.Orientation = 0

                start = (payload["payload"]["startX"], payload["payload"]["startY"])
                end = (payload["payload"]["endX"], payload["payload"]["endY"])
                startDirection = payload["payload"]["startDirection"]
                endDirection = payload["payload"]["endDirection"]
                weight = payload["payload"]["pathWeight"]
                self.link_to_planet.add_path((start, startDirection), (end, endDirection), weight)

            elif payload["type"] == "pathSelect":
                self.Dc = payload["payload"]["startDirection"]
                self.selectedPath = self.Dc

            elif payload["type"] == "target":
                self.Xt = payload["payload"]["targetX"]
                self.Yt = payload["payload"]["targetY"]
                self.link_to_planet.target = (self.Xt, self.Yt)

            elif payload["type"] == "done":
                # finish exploration
                self.finished = True
                self.client.loop_stop()

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.

    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))
        self.client.publish(topic, payload=json.dumps(message), qos=1)
        # print("Message received")

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise

    # testPlanet:remove during exam
    def testplanet(self):
        msg = {
            "from": "client",
            "type": "testplanet",
            "payload": {
                "planetName": "Mehl"
            }
        }
        self.send_message("explorer/112", msg)

    # first message after landing
    def landing_message(self):
        msg = {
            "from": "client",
            "type": "ready"
        }
        self.send_message("explorer/112", msg)
        print("Landing Message sent")

    # message, which path was used
    def path_message(self, xs, ys, ds, input, pathstatus):
        msg = {
            "from": "client",
            "type": "path",
            "payload": {
                "startX": xs,
                "startY": ys,
                "startDirection": ds,
                "endX": input[0],
                "endY": input[1],
                "endDirection": input[2],
                "pathStatus": str(pathstatus)
            }
        }
        self.send_message("planet/" + str(self.planetName) + "/112", msg)
        # print("Path_message sent")

    # message, which one is chosen
    def selected_path_message(self, xs, ys, ds):
        msg = {
            "from": "client",
            "type": "pathSelect",
            "payload": {
                "startX": xs,
                "startY": ys,
                "startDirection": ds
            }
        }
        self.selectedPath = ds
        self.x_backup = xs
        self.y_backup = ys
        self.send_message("planet/" + str(self.planetName) + "/112", msg)

    # message, if target is reached
    def target_reached_message(self):
        msg = {
            "from": "client",
            "type": "targetReached",
            "payload": {
                "message": "Reached Target"
            }
        }
        self.send_message("explorer/112", msg)

    # message, when exploration is completed
    def exploration_completed_message(self):
        msg = {
            "from": "client",
            "type": "explorationCompleted",
            "payload": {
                "message": "Exploration Completed"
            }
        }
        self.send_message("explorer/112", msg)
