import hashlib
import base64
import json
import requests
from datetime import datetime
import calendar
import string
from random import *
import hmac


def __make_request(http_method, path, access_key, secret_key, body):

    # http_method = 'get'                   # get|put|post|delete - must be lowercase
    base_url = 'https://sandboxapi.rapyd.net'
    # path = '/v1/data/countries'           # Portion after the base URL. Hardkeyed for this example.

    # salt: randomly generated for each request.
    min_char = 8
    max_char = 12
    allchar = string.ascii_letters + string.punctuation + string.digits
    salt = "".join(choice(allchar)for x in range(randint(min_char, max_char)))

    # Current Unix time (seconds).
    d = datetime.utcnow()
    timestamp = calendar.timegm(d.utctimetuple())

    # access_key = 'your-access-key'        # The access key received from Rapyd.
    # secret_key = 'your-secret-key'        # Never transmit the secret key by itself.

    # body = ''                             # JSON body goes here. Always empty string for GET; 
                                        # strip nonfunctional whitespace.
    str_body = json.dumps(body, separators=(',', ':'), ensure_ascii=False) if body else ''
    to_sign = http_method + path + salt + str(timestamp) + access_key + secret_key + str_body

    h = hmac.new(bytes(secret_key, 'utf-8'), bytes(to_sign, 'utf-8'), hashlib.sha256)

    signature = base64.urlsafe_b64encode(str.encode(h.hexdigest()))

    url = base_url + path

    headers = {
        'access_key': access_key,
        'signature': signature,
        'salt': salt,
        'timestamp': str(timestamp),
        'Content-Type': "application\/json"
    }

    return url, headers
def create_checkout(http_method, path, access_key, secret_key, body):
    url, headers = __make_request(http_method, path, access_key, secret_key, body)
    return requests.post(url, headers = headers, bod=body)