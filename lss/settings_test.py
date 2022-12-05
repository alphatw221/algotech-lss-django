from lss.settings import *

DEBUG = True
TEST = True            
MOCK_SERVICE = True

GCP_API_LOADBALANCER_URL = "http://localhost:8000"
WEB_SERVER_URL = "http://localhost:3000"

SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/cart"

GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "715361967747-fvvrbaf18n412htlb92p8k6558kj4ugi.apps.googleusercontent.com" # for nick test
GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"

STRIPE_API_KEY = "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"

RECAPTCHA_SECRET_KEY='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'


DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'lss',       #django test prefix 'test' automaticly
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb://34.126.92.142:27017, 35.240.200.4:27017, 34.126.155.150:27017',
            'replicaSet': 'rs0',
            'username': 'lss',
            'password': 'algo83111T%%',
            'authSource': 'test_lss',
            'authMechanism': 'SCRAM-SHA-1',
            'readPreference': 'secondaryPreferred',
            'ssl': False,
        }
    },
}

MONGODB_CONNECTION_STRING = \
    'mongodb://'+'lss'+':'+'algo83111T%%'+\
    '@34.126.92.142:27017,35.240.200.4:27017,34.126.155.150:27017/'+\
    '?authSource='+'test_lss'
    
MONGODB_DATABASE_NAME = 'test_lss'


REDIS_SERVER = {
    "host": "127.0.0.1",
    "port": "6379",
    "username": None,
    "password": r"algo83111T%%"}

CACHE_SERVER = {
    "host": "127.0.0.1",
    "port": "6380",
    "username": None,
    "password": r"algo83111T%%"}

