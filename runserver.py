import os

os.environ['RATCHAT_TESTING'] = 'False'

from ratchat import app, socketio

if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app, host='0.0.0.0')
