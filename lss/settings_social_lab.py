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
WEB_SERVER_URL = "https://plusone.sociallab.ph"
# GCP_API_LOADBALANCER_URL = "https://sb.liveshowseller.ph"
GCP_API_LOADBALANCER_URL = "https://plusone.sociallab.ph"
SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/cart"
REDIS_SERVER = {
    "host": "52.76.83.75",
    "port": "6379",
    "username": None,
    "password": r"1234"
}
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': 
        {
            # "hosts": [('127.0.0.1', 6379)],
            "hosts": [r"redis://:1234@52.76.83.75:6379/0"],
        }
        ,
    },
}


GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "1085297007024-jvsbalojljt87t84cu3vqum28pulhlsd.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"

# mail app
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sociallab.ph'  # smtp.gmail.com
EMAIL_PORT = 465
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'no-reply@sociallab.ph'
EMAIL_HOST_PASSWORD = 'b1722fc%c)#3'

FACEBOOK_APP_CREDS = {
    "name": "PlusOne+1",
    "app_id": "328795722662791",
    "app_secret": "cf1b40e83bfa5f6afb545e2ba5534d29",
}
CHAT_BOT_FACEBOOK = {
    'VERIFY_TOKEN': 'SOCIALLABPLUSONEMESSENGER'
}
WORDPRESS_WEBHOOK_SECRET = '}:`o1k$UoF767:RQO^+mW(9D7!O*Hst*?#<X&bLOINz[ro#F6k'

# template global value
LOGO_URL = GOOGLE_STORAGE_STATIC_DIR + "LSSlogo-300-172.png"
NOTIFICATION_EMAIL = 'lss@algotech.app'