import time
import unittest
from urllib.request import urlopen
from flask import Flask, session
from fakeredis import FakeStrictRedis

from ratchat import app, socketio, redis_db
from utils import noisy_print, create_db



class SocketTestCase(unittest.TestCase):

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

    def get_relevant(self, string, received):
        for x in received:
            if x.get('name') == string:
                return x



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



class TestChatSockets(SocketTestCase):

    def test_connect(self):
        client = socketio.test_client(app)
        received = client.get_received()
        assert len(received) > 0
        client.disconnect()

    def test_messages_are_broadcasted(self):
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        client1.get_received()
        client2.get_received()

        client1.emit('chat_message', { 'msg': "test message" })
        received1 = self.get_relevant('chat_message', client1.get_received())
        received2 = self.get_relevant('chat_message', client2.get_received())
        self.assertEqual(received1['args'][0]['msg'], "test message")
        self.assertEqual(received2['args'][0]['msg'], "test message")

        client1.disconnect()
        client2.disconnect()

    def test_active_users_sent_on_connect(self):
        client = socketio.test_client(app)

        received = client.get_received()
        active_users_msg = self.get_relevant('active_users', received)

        assert len(active_users_msg) > 0
        client.disconnect()

    def test_asssigned_usernames_are_unique(self):
        names = set([])
        for i in range(5):
            client = socketio.test_client(app)
            received = client.get_received()
            user_joined_msg = self.get_relevant('user_joined', received)
            names.add(user_joined_msg['args'][0])
            session = socketio.server.environ[client.sid]['saved_session']
            client.disconnect()
            session['uid'] = None
        self.assertEqual(len(names), 5)

    def test_broadcast_message_when_user_joins(self):
        client1 = socketio.test_client(app)
        client1.get_received()
        client2 = socketio.test_client(app)

        received = client1.get_received()
        user_joined_msg = self.get_relevant('user_joined', received)
        assert user_joined_msg is not None

        client1.disconnect()
        client2.disconnect()

    def test_chat_loads_with_recent_messages(self):
        client1 = socketio.test_client(app)
        client1.emit('chat_message', {'msg': 'Hello Room'})
        client2 = socketio.test_client(app)
        received = client2.get_received()
        recent_messages_msg = self.get_relevant('recent_messages', received)
        self.assertEqual(recent_messages_msg['name'], 'recent_messages')


class TestChatRooms(SocketTestCase):

    def test_personal_room_assigned_on_login(self):
        client = socketio.test_client(app)
        received = client.get_received()
        uid_message = self.get_relevant('testing_uid', received)
        uid = uid_message['args'][0]['uid']
        socketio.emit('test_emission', {}, room=uid)
        received = client.get_received()
        client.disconnect()
        assert self.get_relevant('test_emission', received) is not None

    def test_private_message(self):
        client1 = socketio.test_client(app)
        client1.get_received()
        client2 = socketio.test_client(app)
        
        received1 = client1.get_received()
        user_joined_msg = self.get_relevant('user_joined', received1)
        client2_name = user_joined_msg['args'][0]

        client2.get_received()
        client1.emit('chat_message', {'msg': '/msg ' 
                                      + client2_name 
                                      + ' Hello there'})
        received = client2.get_received()

        client1.disconnect()
        client2.disconnect()

        assert self.get_relevant('private_message', received) is not None


    def test_join_room(self):
        pass

    def test_create_room(self):
        pass


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

    def test_db_logs_messages(self):
        client = socketio.test_client(app)
        client.emit('chat_message', {'msg': 'Are you logging?'})
        db_msgs = redis_db.zrange('messages:global', 0, 10)
        assert len(db_msgs) == 1
        message_id = db_msgs[0].decode()
        msg_content = redis_db.hget('message:' + message_id, 'msg').decode()
        self.assertEqual(msg_content, 'Are you logging?')
        client.disconnect()


