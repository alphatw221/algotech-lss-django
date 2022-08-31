from ._config import db
from ._config import Collection
from bson.json_util import loads, dumps

__collection = db.api_user_subscription


class UserSubscription(Collection):

    _collection = db.api_user_subscription
    collection_name='api_user_subscription'

from pprint import pprint
def get_user_subscription_campaign_count():

    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":{"$ne":None}}},

        {
            "$lookup": {
                "from": "api_user_subscription_facebook_pages",
                "as": "facebook_pages", # "localField": "id","foreignField": "user_subscription_id",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$user_subscription_id"] },
                        "id":{"$ne":None}}
                     },
                    {"$project":{"_id":0,"count":{"$sum":1}}},
                ]
            },
        },

        
        {"$project":{"_id":0,"facebook_page_count":{"$sum":"$facebook_pages.count"}, "name":1, "id":1 }},

        # {
        #     "$lookup": {
        #         "from": "api_campaign",
        #         "as": "campaigns", # "localField": "id","foreignField": "user_subscription_id",
        #         'let': {'id': "$id" },
        #         "pipeline":[
        #             {"$match":{
        #                 '$expr': { '$eq': ["$$id", "$user_subscription_id"] },
        #                 "id":{"$ne":None}}
        #              },
        #             {"$project":{"_id":0,"count":{"$sum":1}}},
        #         ]
        #     },
        # },
        # {"$project":{"_id":0,
        #     "name":1,
        #     "id":1,
        #     "campaign_count":{"$sum":"$campaigns.count"},
        # }},
    ])
    l = list(cursor)
    pprint(l)


def get_user_subscription_from_dealer(dealer_id):
    filter_query = {'$expr': { '$eq': ["$$id", "$user_subscription_id"] },"id":{"$ne":None} }
    
    query = [
        {"$match":{"dealer_id":dealer_id}},
        # {"$lookup":{
        #     "from": "api_user","as": "users",
        #     "localField": "id",
        #     "foreignField": "user_subscription_id",
        #     "pipeline":[
        #         {"$project":{
        #             "_id":0,
        #         }}
        #     ],   
        # }},
        {"$lookup":{
            "from": "api_campaign","as": "campaign",
            "localField": "id",
            "foreignField": "user_subscription_id",
            "pipeline":[
                {"$count":"campaign_count"},
                {"$project":{
                    "_id":0,
                    "id":1,
                    "campaign_count": 1,
                }},
                
            ],   
        }},
        {"$lookup":{
            "from": "api_campaign","as": "campaign",
            "localField": "id",
            "foreignField": "user_subscription_id",
            "pipeline":[
                {"$lookup":{
                    "from":"api_order","as":"order",
                    "localField": "id",
                    "foreignField": "campaign_id",
                    "pipeline":[
                        # {"$project":{
                        #     "_id":1,
                        #     "customer_id":1
                        # }},
                        {"$group":{
                            "_id":"$customer_id",
                            "buyers":{"$sum":1}
                        }},
                        # {"$unwind": "$buyers" },
                        {"$group":{
                            "_id":"$_id",
                            "buyer_count":{"$sum":1}
                            }},
                        # {"$count":"count"},
                        # {"$project":{
                        #     "_id":0,
                        #     "count":1
                        # }}
                    ]
                }}
            ],   
        }},
        # {"$lookup":{
        #     "from":"api_order","as":"order",
        #     "localField": "campaign.id",
        #     "foreignField": "campaign_id",
        #     "pipeline":[
        #         # {"$group":{
        #         #     "_id":"$id",
        #         #     "buyers":{"$addToSet":"$customer_id"},
        #         #     "subtotal":{"$sum":"$subtotal"}
        #         #     }},
        #         # {"$unwind": "$buyers" },
        #         # {"$group":{
        #         #     "_id":"$_id",
        #         #     "buyer_count":{"$sum":1}
        #         #     }},
        #         {"$project":{
        #             "_id":0,
        #             "customer_id":1
        #         }}
        #         # {"$count":"order_count"}
        #     ], 
        # }},
         {"$group":{
            "_id":"$id",
            "id":{"$first":"$id"},
            "campaign_count":{"$first":"$campaign.campaign_count"},
            "users":{"$first":"$users"},
            "buyers":{"$first":"$campaign.order.buyer_count"},
            # "order":{"$first":"$order.subtotal"},
            "sales":{"$first":{"$sum":"$order.subtotal"}}
        }},
        {"$project": {
            "_id":0
        }}
        # { "$unwind": "$campaign" },
    ]
    
    cursor=db.api_user_subscription.aggregate(query)
    
    bson = list(cursor)
    data_str = dumps(bson)
    data_json = loads(data_str)

    
    
    print(data_json)
    
    return data_json