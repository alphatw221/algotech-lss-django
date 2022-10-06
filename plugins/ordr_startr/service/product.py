from .__service import get_header, load_response

from requests import request
import json

def __get_url():
    return 'https://dev.liveorder.thevelocitee.com:9000/api/keywords/FbPage/110577918484495/getAllProducts' #temp
    # return 'https://api.liveorder.ordrstartr.com/api/keywords/FbPage/669953996431156/getAllProducts'  #temp


def get_products(key):

    data = {}

    response = request("GET", __get_url(), 
        headers = get_header(key), 
        json = data,
        timeout=5
    )
    return load_response(response)
