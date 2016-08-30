from flask_socketio import emit, join
from ratchat import app, socketio


command_examples = \
    '/msg otheruser message\n' \
    '/login username password\n'\
    '/register newuser password\n'\
    '/join roomname\n' \
    '/create roomname\n' \
    '/invite username'


def msg(receiver, *message):
    message = ' '.join(message)



def login(username, password):
    pass


def register(username, password):
    pass


def join_room(room):
    pass


def create_room(room):
    pass


def invite_to_room(username):
    pass


command_dict = {
    '/msg': msg,
    '/login': login,
    '/register': register,
    '/join': join_room,
    '/create': create_room,
    '/invite': invite_to_room
}


class InvalidCommandError(Exception):
    pass


def execute_command(command_string):
    chunks = [x.strip() for x in command_string.split(' ') if x]
    command = chunks[0]
    args = chunks[1:]
    if command not in command_dict:
        raise InvalidCommandError
    else:
        try:
            command_dict[command](*args)
        except:
            raise InvalidCommandError

