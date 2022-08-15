from requests import request
import json


def create_checkouts(shop, access_token, line_items):
    data = json.dumps({
        "checkout": {
            'presentment_currency': 'MYR',
            "line_items": line_items,
            'email': 'derekhwang33@gmail.com'
        }
    })

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


def list_checkouts(shop, access_token):
    response = request("GET", 
        f"https://{shop}/api/3.0/checkouts.json", 
        headers = {'EasyStore-Access-Token': access_token}, 
    )

    print(response.text)
    if not response.status_code / 100 == 2:
        return False, None

    return True, json.loads(response.text)
