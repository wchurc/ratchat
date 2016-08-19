from flask import render_template
from flask_socketio import emit, send

from ratchat import app, socketio
from ratchat.name_generator import get_name


@app.route('/')
def main():
    return render_template('index.html')

@socketio.on('connected')
def user_connected(data):
    data['username'] = get_name()
    message = "{} has joined the chat".format(data['username'])
    emit('user_joined', message, broadcast=True)
    emit('assign_username', data)

@socketio.on('chat_message')
def handle_chat_message(message):
    emit('chat_message', message, broadcast=True)

@socketio.on('connect')
def user_connected():
   send('connected-test')
