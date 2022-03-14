from lss.settings import *

DATABASES = {
    # for social lab
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'lss',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb://52.221.239.166:27017, 13.215.51.14:27017, 18.142.57.3:27017',
            'replicaSet': 'rs1',
            'username': 'admin',
            'password': 'admin',
            'authSource': 'admin',
            'authMechanism': 'SCRAM-SHA-1',
            'readPreference': 'primary',
            'ssl': False,
        }
    }
}

MONGODB_CONNECTION_STRING = 'mongodb://admin:admin@52.221.239.166:27017,13.215.51.14:27017,18.142.57.3:27017'
WEB_SERVER_URL = "https://plusone.sociallab.ph/lss/public"

REDIS_SERVER = {
    "host": "127.0.0.1",
    "port": "6379",
    "username": None,
    "password": r"1234"
}

GCP_API_LOADBALANCER_URL = "https://sb.liveshowseller.ph"