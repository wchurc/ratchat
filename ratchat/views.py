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


@socketio.on('connected')
def user_connected(data):
    uid = session.get('uid')
    assert uid
    if not names.get(uid):
        names[uid] = get_name()
    data['username'] = names.get(uid)
    message = "{} has joined the chat".format(data['username'])
    emit('user_joined', message, broadcast=True)
    emit('assign_username', data)


@socketio.on('chat_message')
def handle_chat_message(message):
    emit('chat_message', message, broadcast=True)


@socketio.on('connect')
def user_connected():
   send('connected-test')

