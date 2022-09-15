from .__service import get_header, load_response

from requests import request
import json

def __get_url(shop, order_id=None, created_at_min=None, page=1):
    if order_id:
        return f"https://{shop}/api/3.0/orders/{order_id}.json"
    return f"https://{shop}/api/3.0/orders.json?created_at_min={created_at_min}&financial_status=paid&page={page}"


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

def list_order(shop, access_token, created_at_min, page):
    # data = {**kwargs}
    response = request("GET", __get_url(shop, created_at_min=created_at_min, page=page), 
        headers = get_header(access_token), 
        # json = data,
        timeout=10
    )
    return load_response(response)