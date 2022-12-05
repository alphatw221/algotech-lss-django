from .__service import get_header, load_response

from requests import request
import json
from django.conf import settings

def __get_url():
    # return 'https://dev.liveorder.thevelocitee.com:9000/api/keywords/FbPage/110577918484495/getAllProducts' #temp
    return 'https://api.liveorder.ordrstartr.com/api/keywords/FbPage/669953996431156/getAllProducts'  #temp


def get_products(key):

    if(settings.MOCK_SERVICE):
        return True, [{
            "maxQty": 1,
            "defaultMaxQty": 1,
            "SKU": "test",
            "visible": True,
            "sold": 0,
            "supplierName": "Japan",
            "counter": 0,
            "_id": "123",
            "description": "Cream / Peacoat (Unisex) - EU36",
            "keyword": "test",
            "price": 10,
            "stock": 1,
            "reply_message": "Cream / Peacoat (Unisex) - EU36",
            "FbPageId": "669953996431156",
            "createdAt": "2022-09-25T09:04:36.931Z",
            "updatedAt": "2022-09-25T11:17:57.003Z",
            "__v": 0
        }]
        
    data = {}

    response = request("GET", __get_url(), 
        headers = get_header(key), 
        json = data,
        timeout=5
    )
    return load_response(response)
