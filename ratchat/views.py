from flask import render_template, request, session
from flask_socketio import emit, join_room, send
import uuid
import time

from ratchat import app, socketio, redis_db
from ratchat.name_generator import get_name
from ratchat.exceptions import InvalidNameError, InvalidCommandError
from ratchat.command_parser import execute_command
from ratchat.utils import send_recent_messages, send_active_users, \
                          create_username, unexpire 


@app.route('/')
def main():
    if not session.get('sid'):
        session['sid'] = uuid.uuid4().hex
    return render_template('index.html')


@socketio.on('connect')
def handle_connection():
    send_recent_messages()
    emit('chat_message', {'msg': 'Type /help for a list of commands.',
                          'username': 'server'})
    
    sid = session.get('sid')

    if sid is None:
        session['sid'] = uuid.uuid4().hex
        sid = session.get('sid')
    
    if redis_db.exists(sid):
        unexpire(sid)
    
    if redis_db.get(sid) is None:
        try:
            name = create_username(sid)
        except Exception as e:
            print(e)
            return
        else:
            emit('user_joined', name, broadcast=True)
        finally:
            assert redis_db.get(sid) is not None
    
    send_active_users(broadcast=True)
    join_room(sid)
    emit('testing_sid', {'sid': sid})


@socketio.on('disconnect')
def handle_user_disconnect():
    sid = session.get('sid')
    name = redis_db.get(sid)
    redis_db.srem('active_users', name)

    redis_db.expire(sid, 10)
 
    if redis_db.hget(name, 'registered') == b'False':
        redis_db.expire(name, 10)
    print("Got Disconnect: {} {}".format(name, sid))
    send_active_users(broadcast=True)


@socketio.on('chat_message')
def handle_chat_message(message):
    sid = session['sid']
    if message['msg'][0] == '/':
        try:
            execute_command(sid, message['msg'])
        except InvalidCommandError as e:
            print(e.args)
            emit('chat_message', 
                {'msg': 'Invalid command. Type "/help" for list of commands',
                'username': 'server'},
                room=sid)

    else:
        message['username'] = redis_db.get(sid).decode()
        emit('chat_message', message, broadcast=True)

        msg_id = uuid.uuid4().hex
        redis_db.zadd('messages:global', time.time(), msg_id)
        redis_db.hmset('message:' + msg_id, message)

