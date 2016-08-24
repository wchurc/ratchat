import time
import unittest
from urllib.request import urlopen
from flask import Flask
from fakeredis import FakeStrictRedis

from ratchat import app, socketio, redis_db
from utils import noisy_print, create_db


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
        redis_db.flushall()

    def tearDown(self):
        redis_db.flushall()

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

    def test_chat_loads_with_recent_messages(self):
        client1 = socketio.test_client(app)
        client1.emit('chat_message', {'msg': 'Hello Room'})
        client2 = socketio.test_client(app)
        received = client2.get_received()
        self.assertEqual(received[0]['name'], 'recent_messages')


class TestRedisDB(unittest.TestCase):
    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    def setUp(self):
        redis_db.flushall()

    def tearDown(self):
        redis_db.flushall()

    def test_using_fake_redis_db(self):
        assert isinstance(redis_db, FakeStrictRedis)

    def test_testing_db(self):
        redis_db.set('foo','bar')
        foo = redis_db.get('foo')

        self.assertEqual(foo, b'bar')

    def test_testing_db_gets_cleaned(self):
        self.assertFalse(redis_db.get('foo'))

