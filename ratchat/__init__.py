from flask import Flask
from flask_socketio import SocketIO

from config import development_cfg


app = Flask(__name__)
socketio = SocketIO(app)
app.config.update(development_cfg)

from utils import create_db

redis_db = create_db()

import ratchat.views
