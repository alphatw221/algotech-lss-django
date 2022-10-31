from lss.settings import *
DEBUG = True
# Live Show Seller info
WEB_SERVER_URL = "https://staginglss.accoladeglobal.net"

SHOPPING_CART_URL = f"{WEB_SERVER_URL}/buyer/cart"
# HITPAY_API_URL = 'https://api.sandbox.hit-pay.com/v1/payment-requests' # for test mode
# HITPAY_API_KEY = '64044c7551b232cbf23b32d9b21e30ff1f4c5b42068c8c59864f161cad6af21b' # for test mode
GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "715361967747-fvvrbaf18n412htlb92p8k6558kj4ugi.apps.googleusercontent.com" # for nick test
GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"

# GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "647555482564-u2s769q2ve0b270gnmr5bpqdfmc9tphl.apps.googleusercontent.com" # for lss 2.0 test
# GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER = "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"

# STRIPE_API_KEY = "sk_test_51J2aFmF3j9D00CA0KABMZVKtOVnZNbBvM2hcokicJmfx8vvrmNyys5atEAcpp0Au2O3HtX0jz176my7g0ozbinof00RL4QAZrY"
STRIPE_API_KEY = "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"
#Recaptcha V2
RECAPTCHA_SECRET_KEY='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
