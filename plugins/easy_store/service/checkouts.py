from .__service import get_header, load_response

from requests import request
import json

def __get_url(shop, cart_token=None):
    if cart_token:
        return f"https://{shop}/api/3.0/checkouts/{cart_token}.json"
    return f"https://{shop}/api/3.0/checkouts.json"

def create_checkout(shop, access_token, line_items):
    # print(line_items)
    data = {
        "checkout": {
            "line_items":line_items
        }
    }
    print(data)
    response = request("POST", __get_url(shop), 
        headers = get_header(access_token), 
        json = data,
        timeout=5
    )
    return load_response(response)

def retrieve_checkout(shop, access_token, cart_token):

    data = {}
    response = request("GET", __get_url(shop, cart_token), 
        headers = get_header(access_token), 
        json = data,
        timeout=5
    )
    return load_response(response)

def update_checkout(shop, access_token, line_items, cart_token):

    data = {
        "checkout": {
            "line_items":line_items
        }
    }

    response = request("POST", 
        f"https://{shop}/api/3.0/checkouts.json", 
        headers = {'EasyStore-Access-Token': access_token}, 
        data = data
    )

    print(response)
    print(response.text)
    if not response.status_code / 100 == 2:
        return False, None

    return True, json.loads(response.text)


def update_checkouts(shop, access_token):
    response = request("PUT", 
        f"https://{shop}/api/3.0/checkouts.json/", 
        headers = {'EasyStore-Access-Token': access_token}, 
    )

    print(response.text)
    if not response.status_code / 100 == 2:
        return False, None

    return True, json.loads(response.text)

    
    response = request("PUT", __get_url(shop, cart_token), 
        headers = get_header(access_token), 
        json = data,
        timeout=5
    )
    print(response.status_code)
    print(response.text)
    return load_response(response)
