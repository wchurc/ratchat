from flask import render_template
from ratchat import app, socketio

@app.route('/')
def main():
    return render_template('index.html')

@socketio.on('my event')
def user_connected(data):
    print(data)

@socketio.on('chat_message')
def handle_chat_message(message):
    socketio.emit('chat_message', message, broadcast=True)
