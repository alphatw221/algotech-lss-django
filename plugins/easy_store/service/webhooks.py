from requests import request
import json
from .__service import load_response

def __get_header(token):
    return {
        'Content-Type': 'application/json',
        'Easystore-Access-Token': token
    }
def __get_url(store):
    return f"https://{store}/api/3.0/webhooks.json"


def create_webhook(store, token, topic, url):

    # All Topics:
        # app/uninstall
        # store/update
        # customer/create
        # customer/delete
        # product/create
        # product/update
        # product/delete
        # order/create
        # order/update
        # order/cancel
        # order/paid
        # order/partially_fulfilled
        # refund/create
        # fulfillment/create
        # fulfillment/update
        # currency/create
        # currency/update
        # currency/delete


    payload = json.dumps({
        "webhook": {
            "topic": topic,
            "url": url
        }
    })
    response = request("POST", __get_url(store), headers=__get_header(token), data=payload, timeout=5)
    return load_response(response)

def update_webhook(store, token, topic, url):

    payload = json.dumps({
        "webhook": {
            "topic": topic,
            "url": url
        }
    })
    response = request("PUT", __get_url(store), headers=__get_header(token), data=payload)
    return load_response(response)

def delete_webhook(store, token):

    payload={}
    response = request("DELETE", __get_url(store), headers=__get_header(token), data=payload)
    return load_response(response)