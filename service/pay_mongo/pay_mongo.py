from django.conf import settings
from backend.pymongo.mongodb import db
import hmac, hashlib, base64, binascii
import requests
def create_link(order, secret_key):
    amount = int(order.total * 100)
    print(amount)
    if amount < 10000:
        amount = 10000
    message_bytes = secret_key.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    secret_key = base64_bytes.decode('ascii')

    payload = {
        "data": {
            "attributes": {
                "amount": amount,
                "description": f"Order_{order.id}",
                "remarks": ""
            },
        }
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {secret_key}"
    }

    response = requests.request("POST", f"{settings.PAYMONGO_API_URL}/v1/links", json=payload, headers=headers)
    return response

def register_webhook(secret_key):
    message_bytes = secret_key.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    secret_key = base64_bytes.decode('ascii')

    payload = {"data": {"attributes": {
                "events": ["payment.paid"],
                "url": f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/pay_mongo/webhook/'
            }}}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {secret_key}"
    }

    response = requests.request("POST", f"{settings.PAYMONGO_API_URL}/v1/webhooks", json=payload, headers=headers)
    return response

def retrieve_webhook(secret_key):
    message_bytes = secret_key.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    secret_key = base64_bytes.decode('ascii')
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {secret_key}"
    }

    response = requests.request("GET", f"{settings.PAYMONGO_API_URL}/v1/webhooks", headers=headers)
    return response

def webhook(request):
    order_id = int(request.data['data']['attributes']['data']['attributes']['description'].split('_')[1])
    if (request.data['data']['attributes']['data']['attributes']['status'] == 'paid'):
        db.api_order.update(
            {'id': order_id},
            {'$set': {'status': 'complete'}}
        )