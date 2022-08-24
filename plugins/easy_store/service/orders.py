from .__service import get_header, load_response

from requests import request
import json

def __get_url(shop, order_id=None):
    if order_id:
        return f"https://{shop}/api/3.0/orders/{order_id}.json"
    return f"https://{shop}/api/3.0/orders.json"


def retrieve_order(shop, access_token, order_id):

    data = {}
    response = request("GET", __get_url(shop, order_id), 
        headers = get_header(access_token), 
        json = data,
        timeout=5
    )
    return load_response(response)

def update_order(shop, access_token, data, order_id):

    json = {
        "order": {
            **data
        }
    }
    print(json)
    response = request("PUT", __get_url(shop, order_id), 
        headers = get_header(access_token), 
        json = json,
        timeout=5
    )

    return load_response(response)

def list_order(shop, access_token):
    data = {}
    response = request("GET", __get_url(shop), 
        headers = get_header(access_token), 
        json = data,
        timeout=5
    )
    return load_response(response)