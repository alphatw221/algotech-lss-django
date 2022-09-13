from .__service import get_header, load_response
from requests import request
import json

def __get_url(shop, order_id=None):
    if order_id:
        return f"https://{shop}/admin/api/2022-07/orders/{order_id}.json"
    return f"https://{shop}/admin/api/2022-07/orders.json?status=closed"

def list_order(shop, access_token, **kwargs):
    data = {**kwargs}
    response = request("GET", __get_url(shop), 
        headers = get_header(access_token),
        timeout=5
    )
    return load_response(response)