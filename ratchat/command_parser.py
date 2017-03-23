from flask_socketio import emit, join_room
from ratchat import app, redis_db, socketio
from ratchat.exceptions import InvalidCommandError, InvalidPasswordError
from ratchat.utils import create_username, send_active_users, check_name_length, \
        send_server_msg


def private_message(sender_sid, receiver, *message):
    """Sends a private message to the receiver if receiver is currently
    active."""

    # Check if the receiver is active
    if redis_db.sismember('active_users', receiver) is False:
        send_server_msg("{} is not currently active".format(receiver))
        return

    msg = ' '.join(message)

    try:
        # Get sender's name and receiver's sid from the database
        sender_name = redis_db.get(sender_sid)
        receiver_sid = redis_db.hget(receiver, 'sid')

        if sender_name is None:
            raise Exception('Sender name not found in the database.')

        if receiver_sid is None:
            send_server_msg("I don't know who that is")
            raise Exception('Recipient sid not found in the database.')

        sender_name = sender_name.decode()
        receiver_sid = receiver_sid.decode()

    except Exception as e:
        raise InvalidCommandError(e.args)

    else:
        # Send the message
        data = {'sender': sender_name,
                'receiver': receiver,
                'msg': msg}
        emit('private_message', data, room=receiver_sid)
        emit('private_message', data, room=sender_sid)


def set_temp_name(sid, username):
    """Associates sid with a new temporary username if it's available."""

    if check_name_length(sid, username):
        return

    name_exists = redis_db.exists(username)

    if name_exists:
        send_server_msg('That name is in use.')
        return

    current_name = redis_db.get(sid).decode()

    # Try to create new temp username
    try:
        create_username(sid, name=username)

    except Exception as e:
        raise InvalidCommandError(e.args)

    else:
        # Clean up and delete old name if it was temporary
        if redis_db.hget(current_name, 'registered') == b'False':
            redis_db.delete(current_name)

        redis_db.srem('active_users', current_name)

        send_server_msg('Successfully changed name from: {} to {}'
                        .format(current_name, username))


def login(sid, username, password=None):
    """ Log in as a registered user. If username does not exist
    it will be created."""

    if check_name_length(sid, username):
        return

    # Check if already logged in
    if redis_db.sismember('active_users', username):
        send_server_msg('{} is already logged in'.format(username))
        return

    # Require a password
    if password is None:
        raise InvalidPasswordError('Password is required')

    current_name = redis_db.get(sid).decode()

    try:
        if redis_db.exists(username) is False:
            # Create the username if it doesn't already exist
            create_username(sid, name=username, password=password,
                            registered=True)

        else:
            # Check password
            if password == redis_db.hget(username, 'password').decode():
                # Login
                with redis_db.pipeline() as pipe:
                    pipe.sadd('active_users', username)
                    pipe.set(sid, username)
                    pipe.execute()

            else:
                raise InvalidPasswordError('Password is incorrect')

    except InvalidPasswordError as e:
        send_server_msg('Login failed: ' + e.args[0])

    else:
        # Logout or delete previously used username
        if redis_db.hget(current_name, 'registered') == b'False':
            redis_db.delete(current_name)
        redis_db.srem('active_users', current_name)

        send_server_msg('Login Successful')


def send_help_message(sid):
    msg = "Try the following commands:<br>" \
    '/msg otheruser message<br>' \
    '/login username password<br>' \
    '/callme username<br>' \
    '/help<br>'

    send_server_msg(msg, room=sid)


def join_room(sid, room):
    pass


def create_room(sid, room):
    pass


def invite_to_room(sid, username):
    pass


command_dict = {
    '/msg': private_message,
    '/login': login,
    '/callme': set_temp_name,
    '/join': join_room,
    '/create': create_room,
    '/invite': invite_to_room,
    '/help': send_help_message
}


def execute_command(sid, command_string):
    # Sanity check
    assert sid is not None

    # Parse command
    chunks = [x.strip() for x in command_string.split(' ') if x]
    command = chunks[0]
    args = chunks[1:]

    # Try to execute
    if command not in command_dict:
        raise InvalidCommandError('Unknown command')

    else:
        try:
            command_dict[command](sid, *args)

        except Exception as e:
            print(e.args)
            raise InvalidCommandError(e.args)
