from ratchat import redis_db
from ratchat.name_generator import get_name

from flask_socketio import emit, join_room, send


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
    while name is None:
        name = get_name()
        if not redis_db.exists(name):
            break

    if redis_db.exists(name):
        raise InvalidNameError('Name is in use') # Change this to custom exc?
    

    redis_db.hmset(name, {'sid': sid,
                          'password': password,
                          'registered': registered,
                          'active': active})
    redis_db.set(sid, name)
    return name


def unexpire(sid):
    redis_db.persist(sid)
    name = redis_db.get(sid).decode()
    redis_db.persist(name)
    redis_db.sadd('active_users', name)


def noisy_print(thing):
    if isinstance(thing, dict):
        print('\n' + '>'*50)
        for key in thing:
            print(key,' : ', thing[key])
        print('\n' + '>'*50)

    elif hasattr(thing, '__iter__'):
        print('\n' + '>'*50)
        for x in thing:
            print(x)
        print('\n' + '>'*50)

    else:
        print('\n' + '>'*50 + '\n', thing, '\n' + '<'*50 + '\n')
