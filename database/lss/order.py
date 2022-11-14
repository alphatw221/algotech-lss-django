from ._config import db
from ._config import Collection
from api import models
from bson.json_util import loads, dumps

from pprint import pprint
__collection = db.api_order

def get_oid_by_id(id):
    return str(__collection.find_one({"id":id})['_id'])

class Order(Collection):

    _collection = db.api_order
    collection_name='api_order'
    template = models.order.order.api_order_template


def get_complete_sales_of_campaign(campaign_id):
    
    cursor=__collection.aggregate([
        {"$match":{"campaign_id":campaign_id,"payment_status":models.order.order.PAYMENT_STATUS_PAID }},
        {
            "$group":
                {
                "_id":None,
                "campaign_sales": { "$sum": "$total" },
                }
        },
        {"$project":{"_id":0,"campaign_sales":1}},
    ])

    l = list(cursor)
    return l[0].get('campaign_sales',0) if l else 0

def get_order_export_cursor(pymongo_filter_query, pymongo_sort_by):

        query = [
            {"$match":pymongo_filter_query},
            {
                "$lookup": 
                {
                    "from": "api_order_product",
                    "localField": "id",
                    "foreignField": "order_id",
                    "as": "order_products"
                }
            },
            { "$sort" : pymongo_sort_by},
            { "$unwind":"$order_products" },
            { "$project":{"_id":0,} },
        ]

        cursor=__collection.aggregate(query)
        
        # bson = list(cursor)             
        # # pprint(bson)
        # data_str = dumps(bson)
        # data_json = loads(data_str)    

        return cursor

