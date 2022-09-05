from .__service import get_header, load_response, platform_source_type_map

from requests import request
import json

def __get_url():
    return 'https://dev.liveorder.thevelocitee.com:9000/api/Orders/FbPage/105929794479727/createNewOrder' #temp


def create_order(key, user_id, user_name, platform, product_items):

    data = {
        "User":{
            "Id":user_id,
            "SourceType":platform_source_type_map.get('platform',platform),
            "Name": user_name
        },
        "Items":product_items
    }


    response = request("POST", __get_url(), 
        headers = get_header(key), 
        json = data,
        timeout=5
    )
    return load_response(response)
