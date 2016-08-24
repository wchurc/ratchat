import redis
from ratchat import app


def create_db():

    db = redis.StrictRedis(host=app.config['DB_HOST'],
                           port=app.config['DB_PORT'],
                           password=app.config['DB_PASSWORD'])

    return db
