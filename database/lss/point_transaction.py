from ._config import db
from ._config import Collection
from api import models

from datetime import datetime

__collection = db.api_point_transaction


class PointTransaction(Collection):

    _collection = db.api_point_transaction
    collection_name='api_point_transaction'
    template = models.user.point_transaction.api_point_transaction_template
    
    


def get_wallet_data_with_expired_points(start_from = None, end_at = None):

    point_expired_at_filter_query = {"$ne":None}

    if start_from:
        point_expired_at_filter_query["$gte"] = start_from

    if end_at:
        point_expired_at_filter_query["$lte"] = end_at
    
    query = [
            {"$match":{"expired_at":point_expired_at_filter_query, "buyer_id":{"$ne":None}, "expired_calculated":False}},
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
                    "expired_points_transaction_created_at":{"$first": "$created_at"}
                }
            },
            { "$project":{"_id":0,"user_subscription_id":"$_id.user_subscription_id", "buyer_id":"$_id.buyer_id", "expired_points_transaction_created_at":1} },

        ]

    cursor=__collection.aggregate(query)
    l = list(cursor)
    return l 


def get_earned_used_expired_points_sum(buyer_id, user_subscription_id, point_transaction_created_after=None, ):

    
    query = [
            {"$match":{"buyer_id":buyer_id, "user_subscription_id":user_subscription_id, "created_at":{"$gte":point_transaction_created_after}}},
            
            {
                "$group": {
                    '_id': None,
                    'total_points_earned': { "$sum": "$earned" },
                    'total_points_used': { "$sum": {
                            "$cond": [
                                {
                                    "$or":[
                                        {"$eq": ["$created_at",point_transaction_created_after]},
                                        {"$eq": ["$used_calculated",True]}
                                    ]
                                },
                                0,
                                "$used"
                            ]
                        } },
                    'total_points_expired':{
                        "$sum": {
                            "$cond": [
                                {
                                    "$or":[
                                        {"$gt": ["$expired_at",datetime.utcnow()]},
                                        {"$eq": ["$expired_at",None]},
                                        {"$eq": ["$expired_calculated",True]}
                                    ]
                                },
                                0,
                                "$earned"
                            ]
                        }
                    }
                }
            }
        ]

    cursor=__collection.aggregate(query)
    l = list(cursor)
    return l[0].get('total_points_earned',0) if l else 0, l[0].get('total_points_used',0) if l else 0, l[0].get('total_points_expired',0) if l else 0,

def mark_transaction_points_used_calculated(buyer_id, start_from=datetime.utcnow()):

    __collection.update_many(
        {
            "buyer_id":buyer_id, 
            "created_at":{"$gt":start_from} #use gt here
        },
        {"$set":{"used_calculated":True}})

def mark_transaction_point_expired_calculated(buyer_id, start_from=datetime.utcnow()):

    
    __collection.update_many({
            "buyer_id":buyer_id,
            "created_at":{"$gte":start_from}, #use gte here
            "expired_at":{"$lte":datetime.utcnow()}
        },
        {
            "$set":{"expired_calculated":True}
        })