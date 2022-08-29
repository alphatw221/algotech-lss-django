from requests import request
import json
from .__service import load_response, get_header


def __get_url(shop, webhook_id=None):
    if webhook_id:
        return f"https://{shop}/api/3.0/webhooks/{webhook_id}.json"
    return f"https://{shop}/api/3.0/webhooks.json"


def create_webhook(shop, token, topic, url):

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


    data = {
        "webhook": {
            "topic": topic,
            "url": url
        }
    }
    response = request("POST", __get_url(shop), headers=get_header(token), json=data, timeout=5)
    return load_response(response)

def update_webhook(shop, token, webhook_id, topic, url):

    data = {
        "webhook": {
            "topic": topic,
            "url": url
        }
    }
    response = request("PUT", __get_url(shop, webhook_id), headers=get_header(token), json=data)
    return load_response(response)

def delete_webhook(shop, token, webhook_id):

    payload={}
    response = request("DELETE", __get_url(shop, webhook_id), headers=get_header(token), json=payload)
    return load_response(response)




def list_webhook(shop, token):

    payload={}
    response = request("GET", __get_url(shop), headers=get_header(token), json=payload)
    return load_response(response)



