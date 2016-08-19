import time
import unittest
from urllib.request import urlopen
from flask import Flask
#from flask_testing import TestCase, LiveServerTestCase

from ratchat import app, socketio


class TestChatBasics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_connect(self):
        client = socketio.test_client(app)
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'], 'connected-test')
        client.disconnect()

    def test_messages_are_broadcasted(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client1.get_received()
        client2.get_received()

        client1.emit('chat_message', { 'msg': "test message" })
        received1 = client1.get_received()
        received2 = client2.get_received()
        self.assertEqual(received1[0]['args'][0]['msg'], "test message")
        self.assertEqual(received2[0]['args'][0]['msg'], "test message")

        client1.disconnect()
        client2.disconnect()

    def test_username_is_assigned_on_connect(self):
        client = socketio.test_client(app)
        client.get_received()

        client.emit('connected', {})
        received = client.get_received()
        print(received[1])

        self.assertEqual(received[0]['name'], 'user_joined')
        self.assertEqual(received[1]['args'][0]['username'], 'Reggie Chode')
        client.disconnect()

    def test_broadcast_message_when_user_joins(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client1.get_received()
        client2.get_received()

        client1.emit('connected', {})
        received1 = client1.get_received()
        received2 = client2.get_received()
        self.assertEqual(received2[0]['name'], 'user_joined')

        client1.disconnect()
        client2.disconnect()
