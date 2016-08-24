from flask import render_template, request, session
from flask_socketio import emit, send
import uuid

from ratchat import app, redis_db, socketio
from ratchat.name_generator import get_name


@app.route('/')
def main():
    if not session.get('uid'):
        session['uid'] = uuid.uuid4().hex
    return render_template('index.html')


def send_active_users():
    data = [name.decode() for name in redis_db.hvals('temp_names')]
    emit('active_users', data)


@socketio.on('connect')
def handle_connection():
 #   global names
    uid = session.get('uid')

    if uid is None:
        session['uid'] = uuid.uuid4().hex
        uid = session.get('uid')

    if redis_db.hget('temp_names', uid) is None:
        name = get_name()
        redis_db.hset('temp_names', uid, name)
        joining_user = name
        emit('user_joined', joining_user, broadcast=True)
    send_active_users()


@socketio.on('chat_message')
def handle_chat_message(message):
    uid = session['uid']
    message['username'] = redis_db.hget('temp_names', uid).decode()
    emit('chat_message', message, broadcast=True)

