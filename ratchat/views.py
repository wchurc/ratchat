"""
This module contains Flask and Flask-SocketIO handlers.
"""
import html
import time
import uuid

from flask import render_template, session
from flask_socketio import emit, join_room

from ratchat import app, socketio, redis_db
from ratchat.exceptions import InvalidCommandError
from ratchat.command_parser import execute_command
from ratchat.utils import send_recent_messages, send_active_users, \
        create_username, unexpire, check_timeout, check_msg_length, \
        expire, send_server_msg


thread = None


def active_users_thread():
    """Broadcasts the names of all the users online once every second."""
    while True:
        send_active_users(broadcast=True)
        socketio.sleep(1)


@app.route('/')
def main():
    """Serves the index page of the app and ensures that the session has a
    unique identifier."""
    if not session.get('sid'):
        session['sid'] = uuid.uuid4().hex
    return render_template('index.html')


@socketio.on('connect')
def handle_connection():
    """Handles a SocketIO connection. This must handle brand new sessions or
    a connection after an existing session was interrupted (for example
    the user refreshing the page)"""
    sid = session.get('sid')

    # Check for spamming
    if sid is not None:
        if check_timeout(sid):
            return

    # Send greetings
    send_recent_messages()
    send_server_msg('Type /help for a list of commands.')

    # Make sure there is a valid sid for this session
    if sid is None:
        session['sid'] = uuid.uuid4().hex
        sid = session.get('sid')

    if redis_db.exists(sid):
        unexpire(sid)

    # Make sure this sid has a name
    if redis_db.get(sid) is None:
        try:
            name = create_username(sid)

        except Exception as e:
            print(e)
            return

        else:
            emit('user_joined', name, broadcast=True)

        finally:
            # Sanity check
            assert redis_db.get(sid) is not None

    # Private messages will be sent to the room identified by sid
    join_room(sid)

    # Start the background thread if it doesn't already exist
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=active_users_thread)

    # Send the assigned sid so unit tests can use it
    emit('testing_sid', {'sid': sid})


@socketio.on('disconnect')
def handle_user_disconnect():
    """Handle a SocketIO disconnect event. This has to be recoverable to ensure
    that refreshing the page does not destroy a user's chat session."""
    sid = session.get('sid')
    # Set expiration for temporary data
    expire(sid)


@socketio.on('chat_message')
def handle_chat_message(message):
    """Handles a SocketIO chat_message."""
    sid = session['sid']

    # Check for spamming
    if check_timeout(sid) or check_msg_length(sid, message['msg']):
        return

    # Escape user input
    message['msg'] = html.escape(message['msg'])

    # Handle '/' commands
    if message['msg'][0] == '/':
        try:
            execute_command(sid, message['msg'])

        except InvalidCommandError as e:
            print(e.args)
            send_server_msg('Invalid command. Type "/help" for list of commands',
                            room=sid)

    # Forward chat messages
    else:
        # Send the message
        message['username'] = redis_db.get(sid).decode()
        emit('chat_message', message, broadcast=True)

        # Log the message
        msg_id = uuid.uuid4().hex
        redis_db.zadd('messages:global', time.time(), msg_id)
        redis_db.hmset('message:' + msg_id, message)
