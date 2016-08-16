import unittest
from urllib.request import urlopen
from flask import Flask
#from flask_testing import TestCase, LiveServerTestCase


from ratchat import app, socketio

class TestChat(unittest.TestCase):

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
        print(received)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'], 'connected')
        client.disconnect()
