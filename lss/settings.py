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

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_*%^a_086!sv_#y^t(c0(+%dbqufars4zf8##q!yqjlp#c7m!l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0',
                 "gipassl.algotech.app", '104.199.211.63']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False

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
    'backend',
    'chat_bot',
    'mail',
    'cron',
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
            'filename': os.path.join(BASE_DIR,'_error.log'),
            'formatter': 'standard'
        },
        'file_warning': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR,'_warning.log'),
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
        'DIRS': [],
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
        'NAME': 'lss',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            # Production internal
            # 'host': 'mongodb://10.148.0.7:27017, 10.148.0.8:27017, 10.148.0.9:27017',
            # Production external
            'host': 'mongodb://34.126.92.142:27017, 35.240.200.4:27017, 34.126.155.150:27017',
            'replicaSet': 'rs0',
            'username': 'lss',
            'password': 'algo83111T%%',
            'authSource': 'admin',
            'authMechanism': 'SCRAM-SHA-1',
            'readPreference': 'primary',
            'ssl': False,
        }
    }
}
MONGODB_CONNECTION_STRING = 'mongodb://lss:algo83111T%%@34.126.92.142:27017,35.240.200.4:27017,34.126.155.150:27017'
MONGODB_DATABASE_NAME = 'lss'

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
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Live Show Seller info
WEB_SERVER_URL = "https://place_holder_lss"
SHOPPING_CART_URL = f"{WEB_SERVER_URL}/place_holder_cart"
SUPPORTED_PLATFORMS = [
    ("n/a", "No specific platform"),
    ("facebook", "Facebook"),
    ("youtube", "Youtube"),
    ("instagram", "Instagram"),
]


# Facebook
FACEBOOK_API_URL = "https://graph.facebook.com"
FACEBOOK_APP_CREDS = {
    "name": "Live Show Seller - Algotech",
    "app_id": "967598017063136",
    "app_secret": "e36ab1560c8d85cbc413e07fb7232f99",
}

# Youtube
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
YOUTUBE_API_KEY = "AIzaSyDcsngr4WwNI5HUi9CNMLVRgCx5YdTaaA0"
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

# backend app
COMMENT_PROCESSING = {
    'REST_INTERVAL_SECONDS': 10,
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


# google storage
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'lss_public_bucket'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR,"liveshowseller-b4308e2f9dc6.json")
)
GS_URL = "https://storage.googleapis.com/lss_public_bucket/"

# mail app
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'derekhwang@accoladeglobal.net'
EMAIL_HOST_PASSWORD = 'jyhudyfbvpmewjsc'

# cron app
CRON_CLASSES = [
    # "cron.cron.TestCronJob",
]

# cart lock after shopper access
CART_LOCK_INTERVAL = 180

# redis server
REDIS_SERVER={
    "host":"34.124.140.74",
    "port":"6379",
    "username":None,
    "password":r"algo83111T%%"}
