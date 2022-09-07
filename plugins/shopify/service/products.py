from requests import request
import json


def get_published_product(shop, access_token):

    response = request("GET", f"https://{shop}/admin/api/2022-07/products.json", headers={'X-Shopify-Access-Token': access_token}, timeout=5)

    if not response.status_code / 100 == 2:
        return False, None
    return True, json.loads(response.text)
