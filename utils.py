import redis
from fakeredis import FakeStrictRedis
from ratchat import app

def create_db():

    if app.config['TESTING']:
        db = FakeStrictRedis()

    else:
        db = redis.StrictRedis(host=app.config['DB_HOST'],
                               port=app.config['DB_PORT'],
                               #password=app.config['DB_PASSWORD']
                              )
    return db


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
