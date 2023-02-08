from lss.settings_dev import *
DEBUG = True
WEB_SERVER_URL = "https://localhost:3000"
SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/cart"
SHOPPING_CART_LOGIN_URL = f"{WEB_SERVER_URL}/buyer/login/cart"
# gcp load balancer
GCP_API_LOADBALANCER_URL = "http://localhost:8000"