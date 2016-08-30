from flask import render_template, request, session
from flask_socketio import emit, join_room, send
import uuid
import time

from ratchat import app, redis_db, socketio
from ratchat.name_generator import get_name


@app.route('/')
def main():
    if not session.get('uid'):
        session['uid'] = uuid.uuid4().hex
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
    data = [name.decode() for name in redis_db.hvals('temp_names')]
    emit('active_users', data)


@socketio.on('connect')
def handle_connection():
    send_recent_messages()

    uid = session.get('uid')

    if uid is None:
        session['uid'] = uuid.uuid4().hex
        uid = session.get('uid')

    if redis_db.hget('temp_names', uid) is None:
        name = get_name()
        redis_db.hset('temp_names', uid, name)
        joining_user = name
        emit('user_joined', joining_user, broadcast=True)
    send_active_users()
    join_room(uid)
    emit('testing_uid', {'uid': uid})


@socketio.on('chat_message')
def handle_chat_message(message):
    uid = session['uid']
    username = redis_db.hget('temp_names', uid).decode()
    message['username'] = username
    emit('chat_message', message, broadcast=True)

    msg_id = uuid.uuid4().hex
    redis_db.zadd('messages:global', time.time(), msg_id)
    redis_db.hmset('message:' + msg_id, message)

