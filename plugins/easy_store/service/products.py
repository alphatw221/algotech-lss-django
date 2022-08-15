from requests import request
import json



def get_published_product(shop, access_token, page=1):

    response = request("GET", f"https://{shop}/api/3.0/products.json?visibility=published&page={page}", headers={'EasyStore-Access-Token': access_token}, timeout=5)
    print(response)
    if not response.status_code / 100 == 2:
        return False, None
    return True, json.loads(response.text)


