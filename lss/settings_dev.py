from lss.settings import *

DEBUG = True


MONGODB_CONNECTION_STRING = r'mongodb://lss:algo83111T%%@127.0.0.1:27017'

MONGODB_DATABASE_NAME = 'lss'


# Live Show Seller info
WEB_SERVER_URL = "https://v1login.liveshowseller.com"

SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/login_to_cart"

#NLP
NLP_COMPUTING_MACHINE_URL = "http://192.168.74.127:8501"


GS_URL = "https://storage.googleapis.com/lss_dev_bucket/"


# redis server
REDIS_SERVER = {
    "host": "127.0.0.1",
    "port": "6379",
    "username": None,
    "password": r"algo83111T%%"}


# gcp load balancer
GCP_API_LOADBALANCER_URL = "https://liveshowseller.pagekite.me:8080"

LOCAL_API_SERVER = "http://localhost:8080"
TEST_API_SERVER = "http://localhost:8080"


WEBPACK_LOADER = {
  'DEFAULT': {
    'CACHE': not DEBUG,
    'STATS_FILE': os.path.join(BASE_DIR.parent,'lss_vue/webpack-stats.json'),
    'POLL_INTERVAL': 0.1,
    'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
  }
}
