from .__service import get_header, load_response

from requests import request
import json

def __get_url(shop):
    
    return f"https://{shop}/admin/api/2022-07/draft_orders.json"

def create_checkout(shop, access_token, line_items, discount):
    # print(line_items)
    data = {
        "draft_order":{
            "line_items":line_items,
            "applied_discount":{
                    "description": "Referr discount",
                    "value_type": "fixed_amount",
                    "value": str(discount),
                    "amount": str(discount),
                    "title": "Referr discount"
                } if discount else None
        }
        
    }
    print(data)
    response = request("POST", __get_url(shop), 
        headers = get_header(access_token), 
        json = data,
        timeout=5
    )
    return load_response(response)