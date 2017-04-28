"""
ratchat is a toy web chat app implemented with Flask and SocketIO.
"""
from flask import Flask
from flask_socketio import SocketIO
import fakeredis
import redis

from ratchat.config import config


app = Flask(__name__)
socketio = SocketIO(app)
app.config.update(config)


def create_db():
    """Returns a database connection. If TESTING is set to true in app.config,
    create_db will return a mock connection.
    """

    if app.config['TESTING']:
        db = fakeredis.FakeStrictRedis()

    else:
        db = redis.StrictRedis(host=app.config['DB_HOST'],
                               port=app.config['DB_PORT'],)
    return db


redis_db = create_db()

import ratchat.views
