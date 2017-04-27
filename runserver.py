import os

os.environ['SECRET_KEY'] = str(os.urandom(24))
os.environ['RATCHAT_TESTING'] = 'False'

from ratchat import app, socketio

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
