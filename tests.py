import time
import unittest
from urllib.request import urlopen
from flask import Flask
#from flask_testing import TestCase, LiveServerTestCase

from ratchat import app, socketio
from ratchat.views import names as names_dict


def noisy_print(thing):
    if isinstance(thing, dict):
        print('\n' + '>'*50)
        for key in thing:
            print(key,' : ', thing[key])
        print('\n' + '>'*50)

    elif hasattr(thing, '__iter__'):
        print('\n' + '>'*50)
        for x in thing:
            print(x)
        print('\n' + '>'*50)

    else:
        print('\n' + '>'*50 + '\n', thing, '\n' + '<'*50 + '\n')


class TestChatHTTP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_home_page_exists(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        assert b'<title>ratchat</title>' in rv.data

class TestChatSockets(unittest.TestCase):

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
        self.assertEqual(len(received), 2)
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

    def test_active_users_sent_on_connect(self):
        client = socketio.test_client(app)

        received = client.get_received()

        self.assertEqual(received[1]['name'], 'active_users')
        client.disconnect()

    def test_asssigned_usernames_are_unique(self):
        names = set([])
        for i in range(5):
            client = socketio.test_client(app)
            received = client.get_received()
            names.add(received[0]['args'][0])
            session = socketio.server.environ[client.sid]['saved_session']
            client.disconnect()
            session['uid'] = None
        self.assertEqual(len(names), 5)

    def test_broadcast_message_when_user_joins(self):
        client1 = socketio.test_client(app)
        client1.get_received()
        client2 = socketio.test_client(app)

        received = client1.get_received()
        self.assertEqual(received[0]['name'], 'user_joined')

        client1.disconnect()
        client2.disconnect()


class TestRedisDB(unittest.TestCase):
    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass
