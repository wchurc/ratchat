from flask_socketio import emit, join_room
from ratchat import app, redis_db, socketio
from ratchat.exceptions import InvalidCommandError

command_examples = \
    '/msg otheruser message\n' \
    '/login username password\n'\
    '/register newuser password\n'\
    '/join roomname\n' \
    '/create roomname\n' \
    '/invite username'


def private_message(sender_sid, receiver, *message):    
    msg = ' '.join(message)
    
    try:
        sender_name = redis_db.get(sender_sid)
        receiver_sid = redis_db.hget(receiver, 'sid')
        if sender_name is None:
            raise Exception('Sender name not found in the database.')
        if receiver_sid is None:
            raise Exception('Recipient sid not found in the database.')
    
    except Exception as e:
        raise InvalidCommandError(e.args)
    
    else:    
        data = {'sender': sender_name.decode(),
                'receiver': receiver,
                'msg': msg}
        emit('private_message', data, room=receiver_sid)
        emit('private_message', data, room=sender_sid)


def login(sid, username, password=None):
    # RETHINK THIS
    
    name_exists = redis_db.exists(username)
    
    if name_exists and password is None:
        raise Exception('Username is taken, must enter password')
    
    if name_exists and password is not None:
        if redis_db.hget(username, 'password') != pasword:
            raise Exception('Password is incorrect')
    
    current_name = redis_db.get(sid).decode()
    

    # Update database 

    # Emit confirmation and update chat room
    
    pass


def login_existing():
    pass


def register(sid, username, password):
    pass


def join_room(sid, room):
    pass


def create_room(sid, room):
    pass


def invite_to_room(sid, username):
    pass


command_dict = {
    '/msg': private_message,
    '/login': login,
    '/register': register,
    '/join': join_room,
    '/create': create_room,
    '/invite': invite_to_room
}


def execute_command(sid, command_string):
    chunks = [x.strip() for x in command_string.split(' ') if x]
    command = chunks[0]
    args = chunks[1:]
    if command not in command_dict:
        raise InvalidCommandError
    else:
        try:
            command_dict[command](sid, *args)
        except Exception as e:
            print(e.args)
            raise InvalidCommandError(e.args)

