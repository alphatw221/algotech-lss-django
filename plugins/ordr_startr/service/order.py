from .__service import get_header, load_response, platform_source_type_map

from requests import request
import json

def __get_url():
    # return 'https://dev.liveorder.thevelocitee.com:9000/api/Orders/FbPage/110577918484495/createNewOrder' #temp
    return 'https://api.liveorder.ordrstartr.com/api/Orders/FbPage/669953996431156/createNewOrder'  #temp


def create_order(key, cart_oid, user_id, user_name, platform, product_items):

    data = {
        "User":{
            "Id":user_id,
            "SourceType":platform_source_type_map.get(platform,platform),
            "Name": user_name
        },
        "ExternalReferenceId":cart_oid,
        "Items":product_items
    }
    print(data)

    response = request("POST", __get_url(), 
        headers = get_header(key), 
        json = data,
        timeout=5
    )
    return load_response(response)
