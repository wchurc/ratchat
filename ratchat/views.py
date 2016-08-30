from flask import render_template, request, session
from flask_socketio import emit, join_room, send
import uuid
import time

from ratchat import app, redis_db, socketio
from ratchat.name_generator import get_name
from command_parser import execute_command, InvalidCommandError


@app.route('/')
def main():
    if not session.get('sid'):
        session['sid'] = uuid.uuid4().hex
    return render_template('index.html')


def send_recent_messages():
    recent_message_ids = redis_db.zrange('messages:global', 0, 100, desc=True)
    recent_message_ids.reverse()
    message_list = []
    for message_id in recent_message_ids:
        message = {}
        bytes_message = redis_db.hgetall(b'message:' + message_id)
        message = { key.decode() : value.decode() \
                   for key, value in bytes_message.items() }
        message_list.append(message)
    emit('recent_messages', message_list)


def send_active_users():
    data = [name.decode() for name in redis_db.smembers('active_users')]
    emit('active_users', data)


def create_username(sid, name=None, password=None, registered=False,
                    active=True):
    if name is None:
        name = get_name()
    if redis_db.exists(name):
        raise Exception('Name is in use') # Change this to custom exc.
    redis_db.hmset(name, {'sid': sid,
                          'password': password,
                          'registered': registered})
    redis_db.set(sid, name)
    if active:
        redis_db.sadd('active_users', name)
    return name


def unexpire(sid):
    redis_db.persist(sid)
    name = redis_db.get(sid).decode()
    redis_db.persist(name)
    redis_db.sadd('active_users', name)


@socketio.on('connect')
def handle_connection():
    send_recent_messages()
    
    sid = session.get('sid')

    if sid is None:
        session['sid'] = uuid.uuid4().hex
        sid = session.get('sid')
    else:
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
    
    send_active_users()
    join_room(sid)
    emit('testing_sid', {'sid': sid})


@socketio.on('disconnect')
def handle_disconnect():
    sid = session.get('sid')
    name = redis_db.get(sid)
    redis_db.srem('active_users', name)

    redis_db.expire(sid, 10)
 
    if redis_db.hget(name, 'registered') == b'False':
        redis_db.expire(name, 10)


@socketio.on('chat_message')
def handle_chat_message(message):
    sid = session['sid']
    if message['msg'][0] == '/':
        try:
            execute_command(message['msg'])
        except InvalidCommandError:
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

