from flask import render_template, request, session
from flask_socketio import emit, send
import uuid

from ratchat import app, socketio
from ratchat.name_generator import get_name

names = {}

@app.route('/')
def main():
    if not session.get('uid'):
        session['uid'] = uuid.uuid4()
    return render_template('index.html')


@socketio.on('connect')
def handle_connection():
    data = {}
    uid = session.get('uid')

    if not uid:
        session['uid'] = uuid.uuid4() # had to add for socketio test client
        uid = session.get('uid')

    if not names.get(uid):
        names[uid] = get_name()
        joining_user = names[uid]
        emit('user_joined', joining_user, broadcast=True)
    data['username'] = names.get(uid)
    emit('assign_username', data)


@socketio.on('chat_message')
def handle_chat_message(message):
    emit('chat_message', message, broadcast=True)

