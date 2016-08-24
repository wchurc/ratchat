from flask import render_template, request, session
from flask_socketio import emit, send
import uuid

from ratchat import app, redis_db, socketio
from ratchat.name_generator import get_name

names = {}

@app.route('/')
def main():
    if not session.get('uid'):
        session['uid'] = uuid.uuid4().hex
    return render_template('index.html')


def send_active_users():
    data = [val for val in names.values()]
    emit('active_users', data)


@socketio.on('connect')
def handle_connection():
    global names
    uid = session.get('uid')

    if uid is None:
        session['uid'] = uuid.uuid4().hex
        uid = session.get('uid')

    if names.get(uid) is None:
        names[uid] = get_name()
        joining_user = names[uid]
        emit('user_joined', joining_user, broadcast=True)
    send_active_users()


@socketio.on('chat_message')
def handle_chat_message(message):
    uid = session['uid']
    message['username'] = names[uid]
    emit('chat_message', message, broadcast=True)

