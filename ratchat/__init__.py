from flask import Flask
from flask_socketio import SocketIO
import fakeredis
import redis

from ratchat.config import development_cfg


app = Flask(__name__)
socketio = SocketIO(app)
app.config.update(development_cfg)

def create_db():

    if app.config['TESTING']:
        db = fakeredis.FakeStrictRedis()

    else:
        db = redis.StrictRedis(host=app.config['DB_HOST'],
                               port=app.config['DB_PORT'],
                               #password=app.config['DB_PASSWORD']
                              )
    return db

redis_db = create_db()

import ratchat.views
