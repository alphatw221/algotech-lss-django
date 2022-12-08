from ._config import db
from ._config import Collection
from api import models
from bson.json_util import loads, dumps

from pprint import pprint
from datetime import datetime

__collection = db.api_order

def get_oid_by_id(id):
    return str(__collection.find_one({"id":id})['_id'])

class Order(Collection):

    _collection = db.api_order
    collection_name='api_order'
    template = models.order.order.api_order_template


def get_complete_sales_of_campaign(campaign_id):
    if campaign_id:
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
    return 0
def get_proceed_sales_of_campaign(campaign_id):
    if campaign_id:
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
    return 0
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

def get_wallet_data_with_expired_points(start_from = None, end_at = None):

    point_expired_at_filter_query = {"$ne":None}

    if start_from:
        point_expired_at_filter_query["$gte"] = start_from

    if end_at:
        point_expired_at_filter_query["$lte"] = end_at
    
    query = [
            {"$match":{"point_expired_at":point_expired_at_filter_query, "buyer_id":{"$ne":None}, "point_expired_calculated":False}},
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
            {"$sort":{"created_at":1}},

            {
                "$group":{
                    "_id": {
                        "user_subscription_id": "$user_subscription.id",
                        "buyer_id": "$buyer.id"
                    },
                    "expired_points_order_created_at":{"$first": "$created_at"}
                }
            },
            { "$project":{"_id":0,"user_subscription_id":"$_id.user_subscription_id", "buyer_id":"$_id.buyer_id", "expired_points_order_created_at":1} },

        ]

    cursor=__collection.aggregate(query)
    l = list(cursor)
    return l 


def get_earned_used_expired_points_sum(buyer_id, user_subscription_id, order_created_after=None, ):

    
    query = [
            {"$match":{"buyer_id":buyer_id, "user_subscription_id":user_subscription_id, "created_at":{"$gte":order_created_after}}},
            
            {
                "$group": {
                    '_id': None,
                    'total_points_earned': { "$sum": "$points_earned" },
                    'total_points_used': { "$sum": {
                            "$cond": [
                                {
                                    "$or":[
                                        {"$eq": ["$created_at",order_created_after]},
                                        {"$eq": ["$points_used_calculated",True]}
                                    ]
                                },
                                0,
                                "$points_used"
                            ]
                        } },
                    'total_points_expired':{
                        "$sum": {
                            "$cond": [
                                {
                                    "$or":[
                                        {"$gt": ["$point_expired_at",datetime.utcnow()]},
                                        {"$eq": ["$point_expired_at",None]},
                                        {"$eq": ["$point_expired_calculated",True]}
                                    ]
                                },
                                0,
                                "$points_earned"
                            ]
                        }
                    }
                }
            }
        ]

    cursor=__collection.aggregate(query)
    l = list(cursor)
    return l[0].get('total_points_earned',0) if l else 0, l[0].get('total_points_used',0) if l else 0, l[0].get('total_points_expired',0) if l else 0,

def mark_order_points_used_calculated(buyer_id, start_from=datetime.utcnow()):

    __collection.update_many(
        {
            "buyer_id":buyer_id, 
            "created_at":{"$gt":start_from} #use gt here
        },
        {"$set":{"points_used_calculated":True}})

def mark_order_point_expired_calculated(buyer_id, start_from=datetime.utcnow()):

    
    __collection.update_many({
            "buyer_id":buyer_id,
            "created_at":{"$gte":start_from}, #use gte here
            "point_expired_at":{"$lte":datetime.utcnow()}
        },
        {
            "$set":{"point_expired_calculated":True}
        })


def get_wallet_data(start_from = None, end_at = None ):

    query = [
            {"$match":{"user_subscription_id":{"$ne":None}, "buyer_id":{"$ne":None}, "created_at":{"$gt":start_from, "$lt":end_at }}},
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
def get_anonymous_buyers_data(user_subscription_id):
    query = [
        {
            "$match":{
                "user_subscription_id": user_subscription_id,
                "buyer_id":{'$eq':None}
            },
        },
        {
            "$group": {
                '_id':None,
                'order_id_list': {'$addToSet': '$id'},
            }
        }
    ]
    cursor = __collection.aggregate(query)
    return list(cursor)[0].get('order_id_list', [])

def get_registered_buyers_data(user_subscription_id):
    query = [
        {
            "$match":{
                "user_subscription_id": user_subscription_id,
                "buyer_id":{'$ne':None}
            }
        },
        {
            '$group': {
                '_id': '$buyer_id',
                'order_id': {'$last':'$id'}
                
            }
        },
        {
            "$project": {
                '_id':0,
                'order_id': '$order_id'
            }
        },
        {
            "$group": {
                '_id':None,
                'order_id_list': {'$addToSet': '$order_id'},
            }
        }
    ]
    cursor = __collection.aggregate(query)
    return list(cursor)[0].get('order_id_list', [])
