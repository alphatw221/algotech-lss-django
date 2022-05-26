from lss.settings import *
DEBUG = True
GCP_API_LOADBALANCER_URL = "http://localhost:8001"
WEB_SERVER_URL = "https://localhost/algotech_lss/public"
# for social lab
# WEB_SERVER_URL = "https://plusone.sociallab.ph/lss/public"

SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/login_to_cart"
# HITPAY_API_URL = 'https://api.sandbox.hit-pay.com/v1/payment-requests' # for test mode
# HITPAY_API_KEY = '64044c7551b232cbf23b32d9b21e30ff1f4c5b42068c8c59864f161cad6af21b' # for test mode
# GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "647555482564-u2s769q2ve0b270gnmr5bpqdfmc9tphl.apps.googleusercontent.com" fpr dereck
# GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"
GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "715361967747-fvvrbaf18n412htlb92p8k6558kj4ugi.apps.googleusercontent.com" # for nick test
GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"