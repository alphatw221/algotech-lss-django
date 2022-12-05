from os import access
from requests import request
from .__service import get_header, load_response
import json

def __get_url(shop):
    return f"https://{shop}/admin/api/2022-07/products.json?status=active"

def get_published_product(shop, access_token):

    response = request("GET", __get_url(shop), headers=get_header(access_token), timeout=5)
    return load_response(response)
    # if not response.status_code / 100 == 2:
    #     return False, None
    # return True, json.loads(response.text)
