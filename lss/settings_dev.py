from lss.settings import *
DEBUG = True

# Live Show Seller info
WEB_SERVER_URL = "https://staginglss.accoladeglobal.net"
SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/cart"


# gcp load balancer
GCP_API_LOADBALANCER_URL = "https://staginglss.accoladeglobal.net"


# HITPAY_API_URL = 'https://api.sandbox.hit-pay.com/v1/payment-requests' # for test mode
# HITPAY_API_KEY = '64044c7551b232cbf23b32d9b21e30ff1f4c5b42068c8c59864f161cad6af21b' # for test mode
GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "715361967747-fvvrbaf18n412htlb92p8k6558kj4ugi.apps.googleusercontent.com" # for nick test
GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"


# STRIPE_API_KEY = "sk_test_51J2aFmF3j9D00CA0KABMZVKtOVnZNbBvM2hcokicJmfx8vvrmNyys5atEAcpp0Au2O3HtX0jz176my7g0ozbinof00RL4QAZrY"
STRIPE_API_KEY = "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"
#Recaptcha V2
RECAPTCHA_SECRET_KEY='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'lss_dev',       
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb://34.126.92.142:27017, 35.240.200.4:27017, 34.126.155.150:27017',
            'replicaSet': 'rs0',
            'username': config.MONGO_DB_USERNAME,
            'password': config.MONGO_DB_PASSWORD,
            'authSource': 'lss_dev',
            'authMechanism': 'SCRAM-SHA-1',
            'readPreference': 'secondaryPreferred',
            'ssl': False,
        }
    },
}

MONGODB_CONNECTION_STRING = \
    'mongodb://'+config.MONGO_DB_USERNAME+':'+config.MONGO_DB_PASSWORD+\
    '@34.126.92.142:27017,35.240.200.4:27017,34.126.155.150:27017/'+\
    '?authSource=lss_dev'
    
MONGODB_DATABASE_NAME = 'lss_dev'


REDIS_SERVER = {
    "host": "35.194.149.116",
    "port": "6379",
    "username": None,
    "password": r"lss_dev"}

CACHE_SERVER = {
    "host": "35.194.149.116",
    "port": "6380",
    "username": None,
    "password": r"lss_dev"}

# google storage
GS_BUCKET_NAME = 'lss_dev_bucket'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, "liveshowseller-b4308e2f9dc6.json")
)
GS_URL = "https://storage.googleapis.com/lss_dev_bucket/"
GOOGLE_STORAGE_STATIC_DIR=GS_URL+'static/'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': 
        {
            "hosts": [r"redis://:lss_dev@35.194.149.116:6379/0"],
        }
        ,
    },
}