from lss.settings import *
DATABASES = {
    # for social lab
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'lss',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb://13.215.51.14:27017, 18.142.57.3:27017',
            'replicaSet': 'rs1',
            'username': 'admin',
            'password': 'social=lab$2022%%',
            'authSource': 'admin',
            'authMechanism': 'SCRAM-SHA-1',
            'readPreference': 'primary',
            'ssl': False,
        }
    }
}

MONGODB_CONNECTION_STRING = 'mongodb://admin:social=lab$2022%%@13.215.51.14:27017,18.142.57.3:27017'
WEB_SERVER_URL = "https://plusone.sociallab.ph/lss/public"
SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/login_to_cart"
REDIS_SERVER = {
    "host": "127.0.0.1",
    "port": "6379",
    "username": None,
    "password": r"1234"
}

GCP_API_LOADBALANCER_URL = "https://sb.liveshowseller.ph"

GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "1085297007024-jvsbalojljt87t84cu3vqum28pulhlsd.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"