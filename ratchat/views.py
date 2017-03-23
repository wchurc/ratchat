import html
import time
import uuid

from flask import render_template, request, session
from flask_socketio import emit, join_room, send

from ratchat import app, socketio, redis_db
from ratchat.name_generator import get_name
from ratchat.exceptions import InvalidNameError, InvalidCommandError
from ratchat.command_parser import execute_command
from ratchat.utils import send_recent_messages, send_active_users, \
        create_username, unexpire, check_timeout, check_msg_length, \
        expire


thread = None


def active_users_thread():
    # Broadcast the names of all the users online once every second
    while True:
        send_active_users(broadcast=True)
        socketio.sleep(1)


@app.route('/')
def main():
    # Store a sid in the session if one doesn't already exist and serve index
    if not session.get('sid'):
        session['sid'] = uuid.uuid4().hex
    return render_template('index.html')


@socketio.on('connect')
def handle_connection():
    sid = session.get('sid')

    # Check for spamming
    if sid is not None:
        if check_timeout(sid):
            return

    # Send greetings
    send_recent_messages()
    emit('chat_message', {'msg': 'Type /help for a list of commands.',
                          'username': 'server'})

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
    # Set expiration for temporary data in the database rather than removing it
    # immediately. This way the data won't be deleted if the page is refreshed.
    sid = session.get('sid')
    expire(sid)


@socketio.on('chat_message')
def handle_chat_message(message):
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
            emit('chat_message',
                {'msg': 'Invalid command. Type "/help" for list of commands',
                'username': 'server'},
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

