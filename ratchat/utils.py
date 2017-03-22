from flask_socketio import emit, join_room, send

from ratchat import app, redis_db, socketio
from ratchat.name_generator import get_name
from ratchat.exceptions import InvalidNameError


def send_recent_messages(count=100):
    """
    Used on a new connection to send the 'count' most recent chat messages
    to the connected user.
    """

    recent_message_ids = redis_db.zrange('messages:global', 0, count, desc=True)
    recent_message_ids.reverse()
    message_list = []
    for message_id in recent_message_ids:
        message = {}
        bytes_message = redis_db.hgetall(b'message:' + message_id)
        message = { key.decode() : value.decode() \
                   for key, value in bytes_message.items() }
        message_list.append(message)
    emit('recent_messages', message_list)


def send_active_users(broadcast=False):
    """
    Sends a list of names in the 'active_users' set.
    """

    data = [name.decode() for name in redis_db.smembers('active_users')]
    socketio.emit('active_users', data, broadcast=broadcast)


def create_username(sid, name=None, password=None, registered=False,
                    active=True):
    """
    Creates a new unique name for the given sid. Will use get_name
    if no name is provided.
    """

    while name is None:
        try_name = get_name()
        if not redis_db.exists(try_name):
            name = try_name

    if redis_db.exists(name):
        raise InvalidNameError('Name is in use')

    redis_db.hmset(name, {'sid': sid,
                          'password': password,
                          'registered': registered})
    redis_db.set(sid, name)
    redis_db.sadd('active_users', name)
    return name


def unexpire(sid):
    """
    Persists database keys and adds the name associated with the given sid
    to the active_users set. Used to recover from unintentional disconnects.
    """

    redis_db.persist(sid)
    name = redis_db.get(sid).decode()
    redis_db.persist(name)
    redis_db.sadd('active_users', name)


def check_timeout(sid):
    """
    Keeps track of the number of socket messages emitted by a particular
    user. If number of messages sent in the past MSG_LIMIT_TIMEOUT seconds
    exceeds MSG_LIMIT then the user will be disconnected.
    Returns True if the limit was exceeded.
    """
    return False


def check_msg_length(sid, msg):
    """
    Checks message length against MAX_MSG_LENGTH. Emits a notification
    to the user that the message length was exceeded.
    Returns True if the limit was exceeded.
    """
    if len(msg) > app.config['MAX_MSG_LENGTH']:
        # Send notification
        emit('chat_message',
            {'msg': 'Message exceeded max length!',
            'username': 'server'},
            room=sid)

        return True

    return False


def check_name_length(sid, username):
    """
    Checks if name length is > MAX_NAME_LENGTH. Emits a notification
    to the user and returns True if the length was exceeded.
    """
    if len(username) > app.config['MAX_NAME_LENGTH']:
        emit('chat_message',
            {'msg': 'Username exceeds max length!',
            'username': 'server'},
            room=sid)

        return True

    return False


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
