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

def get_proceed_sales_of_campaign(campaign_id):
    
    cursor=__collection.aggregate([
        {
            "$match":{
                "campaign_id":campaign_id,"payment_status":{ 
                    "$in":[
                        models.order.order.PAYMENT_STATUS_AWAITING_CONFIRM,
                        models.order.order.PAYMENT_STATUS_AWAITING_PAYMENT,
                        models.order.order.PAYMENT_STATUS_FAILED
                    ]
                }
            }
        },
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

def get_wallet_with_expired_points(start_from = None, end_at = None):

    point_expired_at_filter_query = {"$ne":None}

    # if start_from:
    #     point_expired_at_filter_query["$gt"] = start_from

    # if end_at:
    #     point_expired_at_filter_query["$lt"] = end_at
    
    query = [
            {"$match":{"point_expired_at":point_expired_at_filter_query, "buyer_id":{"$ne":None}}},
            {
                "$lookup": 
                {
                    "from": "api_user_subscription",
                    "localField": "user_subscription_id",
                    "foreignField": "id",
                    "as": "user_subscription"
                }
            },
            {
                "$lookup": 
                {
                    "from": "api_user",
                    "localField": "buyer_id",
                    "foreignField": "id",
                    "as": "buyer"
                }
            },
            {"$unwind": '$user_subscription'},
            {"$unwind": '$buyer'},
            {
                "$group":{
                    "_id": {
                        "user_subscription_id": "$user_subscription.id",
                        "buyer_id": "$buyer.id"
                    }
                }
            },
            { "$project":{"_id":0,"user_subscription_id":"$_id.user_subscription_id", "buyer_id":"$_id.buyer_id"} },

        ]

    cursor=__collection.aggregate(query)
    l = list(cursor)
    return l 


def get_used_expired_points_sum(buyer_id, user_subscription_id, start_from = None, end_at = None):

    created_at_filter_query = {}
    
    # if start_from:
    #     created_at_filter_query["$gt"] = start_from

    # if end_at:
    #     created_at_filter_query["$lt"] = end_at
    
    query = [
            {"$match":{"buyer_id":buyer_id, "user_subscription_id":user_subscription_id}},
            
            {'$project':{
                '_id':0,
                'points_used':1,

            }},

            {'$project':{

                'test':{"$sum":'$points_used'}
            }}
        ]

    cursor=__collection.aggregate(query)
    l = list(cursor)
    return l 