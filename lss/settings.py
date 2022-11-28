"""
Django settings for lss project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from google.oauth2 import service_account
from corsheaders.defaults import default_headers
import config
import urllib 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_*%^a_086!sv_#y^t(c0(+%dbqufars4zf8##q!yqjlp#c7m!l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEST = False            
MOCK_SERVICE = False           #if true

# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0',
#                  "gipassl.algotech.app", '104.199.211.63']
ALLOWED_HOSTS = ['*']  # Auto Scale testing

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_HEADERS = list(default_headers) + [
    "Access-Control-Allow-Origin",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_cron',
    'api',
    'automation',
    'cron',
    'corsheaders',
    'django_extensions',
    'webpack_loader',
    'channels',
    'api_v2',
    'django_vite',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, '_error.log'),
            'formatter': 'standard'
        },
        'file_warning': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, '_warning.log'),
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['file_error', 'file_warning'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}

# Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    # 'DATETIME_FORMAT': '%s',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lss.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lss.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': config.MONGO_DB_DATABASE_NAME,
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            # Production internal
            # 'host': 'mongodb://10.148.0.7:27017, 10.148.0.8:27017, 10.148.0.9:27017',
            # Production external
            'host': 'mongodb://34.126.92.142:27017, 35.240.200.4:27017, 34.126.155.150:27017',
            'replicaSet': 'rs0',
            'username': config.MONGO_DB_USERNAME,
            'password': config.MONGO_DB_PASSWORD,
            'authSource': config.MONGO_DB_DATABASE_NAME,
            'authMechanism': 'SCRAM-SHA-1',
            'readPreference': 'secondaryPreferred',
            'ssl': False,
        }
    },
    # for social lab
    # 'default': {
    #     'ENGINE': 'djongo',
    #     'NAME': 'lss',
    #     'ENFORCE_SCHEMA': False,
    #     'CLIENT': {
    #         'host': 'mongodb://52.221.239.166:27017, 13.215.51.14:27017, 18.142.57.3:27017',
    #         'replicaSet': 'rs1',
    #         'username': 'admin',
    #         'password': 'admin',
    #         'authSource': 'admin',
    #         'authMechanism': 'SCRAM-SHA-1',
    #         'readPreference': 'primary',
    #         'ssl': False,
    #     }
    # }
}
MONGODB_CONNECTION_STRING = \
    'mongodb://'+config.MONGO_DB_USERNAME+':'+urllib.parse.quote_plus(config.MONGO_DB_PASSWORD)+\
    '@34.126.92.142:27017,35.240.200.4:27017,34.126.155.150:27017/'+\
    '?authSource='+config.MONGO_DB_DATABASE_NAME
    
# for social lab
# MONGODB_CONNECTION_STRING = 'mongodb://admin:admin@52.221.239.166:27017,13.215.51.14:27017,18.142.57.3:27017'
MONGODB_DATABASE_NAME = config.MONGO_DB_DATABASE_NAME
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

LANGUAGES = [
    ('en', 'English'),
    ('zh-hans', 'Simplified Chinese'),
    ('zh-hant', 'Traditional Chinese'),
    ('id', 'Indonesian'),
    ('vi', 'Vietnam')
]

LANGUAGES_CHOICES = [
    ('en', 'English'),
    ('zh_hans', 'Simplified Chinese'),
    ('zh_hant', 'Traditional Chinese'),
    ('id', 'Indonesian'),
    ('vi', 'Vietnam')
]

SUPPORTED_LANGUAGES = {
    'en',
    'zh_hans',
    'zh_hant',
    'id',
    'vi'
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# STATIC_ROOT = os.path.join(BASE_DIR.parent,"lss_vue_enigma/static2")
STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, "static"),
    # os.path.join(BASE_DIR.parent,"lss_vue/static"),
    os.path.join(BASE_DIR.parent,"lss_vue_enigma/static")
]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# gcp load balancer
GCP_API_LOADBALANCER_URL = "https://v2login.liveshowseller.com"


# Live Show Seller info
WEB_SERVER_URL = "https://v2login.liveshowseller.com"


# SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/login_to_cart"
SHOPPING_CART_URL = f"{GCP_API_LOADBALANCER_URL}/buyer/cart"
SHOPPING_CART_RECAPTCHA_URL = f"{GCP_API_LOADBALANCER_URL}/buyer/recaptcha"



# HITPAY_API_URL = 'https://api.sandbox.hit-pay.com/v1/payment-requests' # for test mode
# HITPAY_API_KEY = '64044c7551b232cbf23b32d9b21e30ff1f4c5b42068c8c59864f161cad6af21b' # for test mode

HITPAY_API_URL = 'https://api.hit-pay.com/v1/payment-requests' # for live mode
HITPAY_API_KEY = 'a17041b2c841f88263faaed459e1579a592a431acf8b69e044645d28d4a1c316' # for live mode


HITPAY_SECRET_SALT = '9ntt8RQoPtP9NXlO36aZTpP5wK10vFWbsw45KjaBGNzfYiU75cUJ3LLCEqMLGUO9'

PAYMONGO_SECRET_KEY = 'sk_test_kXkD4NBMYZixy8dJ8GV6br4u'
PAYMONGO_API_URL = 'https://api.paymongo.com'

# Rapyd
RAPYD_ACCESS_KEY="6C1EC9E97851F0675225" # for test
RAPYD_SECRET_KEY="117af5b965d9f0bf7b9aa9b80b3c7c7f6275d4710861478943312241ba7486f5ec87445b9503d8b6" # for test
BASERAPYDAPIURL="https://sandboxapi.rapyd.net" # sand box

#NLP
NLP_COMPUTING_MACHINE_URL = "http://127.0.0.1:8501"

# Facebook
FACEBOOK_API_URL = "https://graph.facebook.com"
FACEBOOK_API_URL_V12 = "https://graph.facebook.com/v12.0/"
FACEBOOK_APP_CREDS = {
    "name": "Live Show Seller - Algotech",
    "app_id": "967598017063136",
    "app_secret": "e36ab1560c8d85cbc413e07fb7232f99",
}

FACEBOOK_TEST_ACOOUNT = {
    "EMAIL": "twadmin@algotech.app",
    "PASSWORD": "algoFB2022"
}

# Instagram
INSTAGRAM_API_URL = "https://graph.instagram.com"

# Youtube
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
# YOUTUBE_API_KEY = "AIzaSyDcsngr4WwNI5HUi9CNMLVRgCx5YdTaaA0"
YOUTUBE_API_KEY = "AIzaSyAoK27UOjKezYRRBriBqL7kUrmXXRYH3Kw"
GOOGLE_API_URL = "https://www.googleapis.com/"
YOUTUBE_API_CONFIG = {
    "web": {
        "project_id": "primeval-nectar-322805",
        "client_id": "936983829411-6lq90ld3vs8f4ksbl4gv7hrjlsgkkqjg.apps.googleusercontent.com",
        "client_secret": "k7xYNAy5P7yc5YtZ-ecQ3Qhc",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    }
}

# twitch
TWITCH_API_URL="https://api.twitch.tv"
TWITCH_OAUTH_URL = "https://id.twitch.tv"
TWITCH_CLIENT_ID = "yh5jhlahkvxz1k4070q6f4zfpvx3oq"
TWITCH_CLIENT_SECRET = "i2q6fe0x6zetvd5fl4r39hsspni77g"

# Google API credentials
GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"

# Tiktok
TIKTOK_APP_ID = "7132396308677001218"
TIKTOK_APP_SECRET = "e76d92bc644166d14c842d15d87a6c48a79e3717"

# backend app
COMMENT_PROCESSING = {
    'REST_INTERVAL_SECONDS': 40,
    'COMMENT_BATCH_SIZE': 300,
    'MAX_RESPONSE_WORKERS': 50,
}
FACEBOOK_COMMENT_CAPTURING = {
    'MAX_CONTINUOUS_REQUEST_TIMES': 10,
    'REST_INTERVAL_SECONDS': 10,
}

# chat_bot app
CHAT_BOT_FACEBOOK = {
    'VERIFY_TOKEN': 'ALGOTECHLSSMESSENGER'
}
#FTP
FTP_STORAGE_LOCATION = "ftp://lssimages@tig.algotech.app:_TqUPZc*CMdG@74.124.210.137:21" #FTP server: ftp.tig.algotech.app
BASE_URL = "https://tig.algotech.app/lssimages/"
FTP_STORAGE_ENCODING = 'utf-8'

# google storage
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'lss_public_bucket'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, "liveshowseller-b4308e2f9dc6.json")
)
GS_URL = "https://storage.googleapis.com/lss_public_bucket/"
GOOGLE_STORAGE_STATIC_DIR=GS_URL+'static/'
# google monitoring
GCP_PROJECT_ID = "liveshowseller"

# mail app
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.liveshowseller.com'  # smtp.gmail.com
EMAIL_PORT = 465
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'noreply@liveshowseller.com'  # derekhwang@accoladeglobal.net
EMAIL_HOST_PASSWORD = 'bq5^82DrrpQ4'  # jyhudyfbvpmewjsc

# cron app
CRON_CLASSES = [
    "cron.cron.CampaignReminderCronJob",
    "cron.uncheckout_cart_reminder.UncheckoutCartReminderCronJob",
    "cron.adjust_wallet_with_expired_points.AdjustWalletWithExpiredPointsCronJob"
]
DJANGO_CRON_DELETE_LOGS_OLDER_THAN = 10

# cart lock after shopper access
CART_LOCK_INTERVAL = 180

# order report download interval
ORDER_REPORT_DOWNLOAD_INTERVAL = 180

# redis server
REDIS_SERVER = {
    "host": "34.124.140.74",
    "port": "6379",
    "username": None,
    "password": r"algo83111T%%"}

CACHE_SERVER = {
    "host": "34.124.140.74",
    "port": "6380",
    "username": None,
    "password": r"algo83111T%%"}

# REDIS_SERVER = {
#     "host": "127.0.0.1",
#     "port": "6379",
#     "username": None,
#     "password": r"algo83111T%%"}



# paypal settings
# package github: https://github.com/paypal/PayPal-Python-SDK

PAYPAL_CONFIG = {
    "mode": "sandbox",
    "client_id": "ASABJtviIflIhkeEH4QBeYuhQoN7RWcPsC6fN-TXIfzhMQ2UDK1raOVd3xBWAmItoAg2WRgI4Nbpde8J",  # it's sandbox
    "client_secret": "EFEGnvXwP8DsSUYF5zoQ5ZkaArtlpzAlgpWJOwBlHRMUP6NwAq8-KmnTv087ihZrAIlyg5VtKo73Wj54",  # it's sandbox
}

# stripe payment
STRIPE_API_KEY = "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"
# STRIPE_API_KEY = "sk_test_51J2aFmF3j9D00CA0KABMZVKtOVnZNbBvM2hcokicJmfx8vvrmNyys5atEAcpp0Au2O3HtX0jz176my7g0ozbinof00RL4QAZrY"

# APPEND_SLASH=False
# OPERATION_CODE_NAME: AGILE
ADMIN_LIST = [1, ]

# for subscription code
FERNET_KEY = '4zQFttQhIuTXZr15hKSEOwndw_VdLg_bQGc_vPRTtb8='


WEBPACK_LOADER = {
  'DEFAULT': {
    'CACHE': not DEBUG,
    'STATS_FILE': os.path.join(BASE_DIR.parent,'lss_vue/webpack-stats.json'),
    'POLL_INTERVAL': 0.1,
    'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
  }
}

# sendinblue api key
SENDINBLUE_API_KEY = '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'


# hubspot client secret
HUBSPOT_CLIENT_SECRET = '06d95fdd-62ae-4973-b5ab-74ae66a310fe'
HUBSPOT_API_KEY = 'e9a347e7-8923-4e09-8e57-3fa6fe6acc8b'

# cc to email
NOTIFICATION_EMAIL = 'lss@algotech.app'


# Channels
ASGI_APPLICATION = 'lss.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': 
        {
            # "hosts": [('127.0.0.1', 6379)],
            "hosts": [r"redis://:algo83111T%%@34.124.140.74:6379/0"],
        }
        ,
    },
}

#vite
DJANGO_VITE_ASSETS_PATH = os.path.join(BASE_DIR.parent,"lss_vue_enigma/static")
DJANGO_VITE_MANIFEST_PATH = os.path.join(BASE_DIR.parent,"lss_vue_enigma/static/manifest.json")
# DJANGO_VITE_STATIC_URL_PREFIX = 'test'
DJANGO_VITE_DEV_MODE = DEBUG


#Recaptcha V2
RECAPTCHA_SECRET_KEY='6LeNPyMhAAAAADlvfRDj_WThJc7pCrFzFFaPgwWz'

# template global value
LOGO_URL = GOOGLE_STORAGE_STATIC_DIR + "LSSlogo-300-172.png"
WELCOME_HEADER__URL = GOOGLE_STORAGE_STATIC_DIR + "Welcome-400x150.jpg"
