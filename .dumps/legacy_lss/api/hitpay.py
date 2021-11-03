from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from api.utilities.api_orm_utilities import *
from api.utilities.api_utilities import *

# Remove this after swagger implemented
from config import connex_app


@ connex_app.route("/hitpay/webhook", methods=['POST'])
# @jwt_required
def hitpay_webhook():
    import hmac
    import hashlib

    data = request.form.to_dict()
    print(data)

    byte_key = bytes(
        '2MUizyJj429NIoOMmTXedyICmbwS1rt6Wph7cGqzG99IkmCV6nUCQ22lRVCB0Rgu', 'UTF-8')
    message = 'payment_id=92965a2d-ece3-4ace-1245-494050c9a3c1&payment_request_id=92965a20-dae5-4d89-a452-5fdfa382dbe1&phone=&amount=599.00&currency=SGD&status=completed'.encode()
    h = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
    print(h)

    return '', 200
