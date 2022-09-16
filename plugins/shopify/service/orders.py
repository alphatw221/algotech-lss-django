from .__service import get_header, load_response
from requests import request
import json

def __get_url(shop, order_id=None, created_at_min=None):
    if order_id:
        return f"https://{shop}/admin/api/2022-07/orders/{order_id}.json"
    return f"https://{shop}/admin/api/2022-07/orders.json?status=open&created_at_min={created_at_min}"

def list_order(shop, access_token, created_at_min=None):
    response = request("GET", __get_url(shop, created_at_min=created_at_min), 
        headers = get_header(access_token),
        timeout=5
    )
    return load_response(response)