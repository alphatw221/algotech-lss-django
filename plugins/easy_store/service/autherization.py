from .__service import  load_response

from requests import request
import json

def __get_url(shop):
    return f"https://{shop}/api/3.0/oauth/access_token.json"

def __get_header():
    return {
        'Content-Type': 'application/json',
    }
    
def exchange_token(shop, code, client_id, client_secret):

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = request("POST", __get_url(shop), 
        headers = __get_header(), 
        json = data,
        timeout=5
    )
    return load_response(response)
