#!/usr/bin/env python3

import unittest.mock
import paho.mqtt.client as mqtt
import uuid

from communication import Communication


class TestRoboLabCommunication(unittest.TestCase):
    @unittest.mock.patch('logging.Logger')
    def setUp(self, mock_logger):
        """
        Instantiates the communication class
        """
        client_id = '112' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
        client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                             clean_session=False,  # We want to be remembered
                             protocol=mqtt.MQTTv311  # Define MQTT protocol version
                             )

        # Initialize your data structure here
        self.communication = Communication(client, mock_logger)

    def test_message_ready(self):
        """
        This test should check the syntax of the message type "ready"
        """
        self.communication.landing_message()

    def test_message_path(self):
        """
        This test should check the syntax of the message type "path"
        """
        self.communication.path_message(0, 5, 0, 1, 2, 0, "free")

    def test_message_path_invalid(self):
        """
        This test should check the syntax of the message type "path" with errors/invalid data
        """
        # self.fail('implement me!')
        pass

    def test_message_select(self):
        """
        This test should check the syntax of the message type "pathSelect"
        """
        self.communication.selected_path_message(0, 1, 0)

    def test_message_complete(self):
        """
        This test should check the syntax of the message type "explorationCompleted" or "targetReached"
        """
        self.communication.exploration_completed_message()


if __name__ == "__main__":
    unittest.main()
