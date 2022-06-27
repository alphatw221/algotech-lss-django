from ._config import db
from ._config import Collection

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
