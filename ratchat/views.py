from flask import render_template, request, session
from flask_socketio import emit, send

from ratchat import app, socketio
from ratchat.name_generator import get_name

names = {}

@app.route('/')
def main():
    return render_template('index.html')


@socketio.on('connected')
def user_connected(data):
    names[request.sid] = get_name()
    print(names)
    data['username'] = names[request.sid]
    message = "{} has joined the chat".format(data['username'])
    emit('user_joined', message, broadcast=True)
    emit('assign_username', data)


@socketio.on('chat_message')
def handle_chat_message(message):
    emit('chat_message', message, broadcast=True)


@socketio.on('connect')
def user_connected():
   send('connected-test')

