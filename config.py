import os

print("In config.py getting environ. Environ: ", os.environ.get('RATCHAT_TESTING'))

testing = False if os.environ.get('RATCHAT_TESTING') == 'False' else True
print('testing set to: ', testing)
development_cfg = {
    'DB_HOST' : '127.0.0.1',
    'DB_PORT' : 6379,
    #'DB_PASSWORD' : 'PASSWD',
    'DEBUG' : True,
    'SECRET_KEY' : 'real secret',
    'TESTING' : testing
}

