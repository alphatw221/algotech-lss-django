from .__service import get_header, load_response

from requests import request
import json
from django.conf import settings

def __get_url():
    return 'https://api.liveorder.ordrstartr.com/api/keywords/FbPage/669953996431156/getAllProducts'  #temp


def get_products(key):

    if(settings.MOCK_SERVICE):
        return True, [{
            "maxQty": 88,
            "defaultMaxQty": 88,
            "SKU": "AA225",
            "visible": True,
            "sold": 0,
            "supplierName": "Japan",
            "counter": 0,
            "_id": "633019a4d21f1b6bfe15bf40",
            "description": "Cream / Peacoat (Unisex) - EU36",
            "keyword": "AA225",
            "price": 198,
            "stock": 2,
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
