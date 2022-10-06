from ._config import db
from ._config import Collection
from api import models

__collection = db.api_user_subscription


class UserSubscription(Collection):

    _collection = db.api_user_subscription
    collection_name='api_user_subscription'
    template = models.user.user_subscription.api_user_subscription_template
    
from pprint import pprint
def get_campaign_count():

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


def get_order_complete_proceed_count(user_subscription_id):

    cursor=__collection.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","as": "campaigns", # "localField": "id","foreignField": "user_subscription_id",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$user_subscription_id"] },
                        "id":{"$ne":None}}
                     },
                    {
                        "$lookup": {
                            "from": "api_order","as": "orders", # "localField": "id","foreignField": "campaign_id",
                            'let': {'id': "$id" },
                            "pipeline":[
                                {"$match":{
                                    '$expr': { '$eq': ["$$id", "$campaign_id"] },
                                    "id":{"$ne":None}}
                                 },
                                {"$project":{"_id":0,
                                "complete": {  "$cond": [ { "$in":["$status", ["complete", "shipping out"] ] }, 1, 0]},
                                "review": { "$cond": [ { "$eq": [ "$status", "review" ] }, 1, 0]}
                                }},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"id":1,"orders":1,"campaign_complete_count":{"$sum":"$orders.complete"},"campaign_review_count":{"$sum":"$orders.review"}}}
                ]
            },
        },
        {"$project":{"_id":0,
        # "campaigns":1,
        "total_complete_count":{"$sum":"$campaigns.campaign_complete_count"},
        "total_review_count":{"$sum":"$campaigns.campaign_review_count"}
        }}
    ])
    l = list(cursor)
    return l[0].get('total_complete_count',0) if l else 0,\
        l[0].get('total_review_count',0) if l else 0

    

def get_pre_order_count(user_subscription_id):

    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","as": "campaigns", # "localField": "id","foreignField": "user_subscription_id",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$user_subscription_id"] },
                        "id":{"$ne":None}}
                     },
                    {
                        "$lookup": {
                            "from": "api_pre_order","as": "pre_orders", # "localField": "id","foreignField": "campaign_id",
                            'let': {'id': "$id" },
                            "pipeline":[
                                {"$match":{
                                    '$expr': { '$eq': ["$$id", "$campaign_id"] },
                                    "id":{"$ne":None},
                                    "subtotal":{"$ne":0}}
                                 },
                                {"$project":{"_id":0, "count":{"$sum":1}}}
                            ]
                        },
                    },
                    {"$project":{"_id":0, "id":1,"pre_orders":1, "campaign_count":{"$sum":"$pre_orders.count"}}}
                ]
            },
        },
        {"$project":{"_id":0,
        # "campaigns":1,
        "total_count":{"$sum":"$campaigns.campaign_count"}
        }}
    ])
    l = list(cursor)
    return l[0].get('total_count',0) if l else 0


def get_average_sales(user_subscription_id):
    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","as": "campaigns", # ,"localField": "id","foreignField": "user_subscription_id"
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$user_subscription_id"] },
                        "id":{"$ne":None}}
                     },
                    {
                        "$lookup": {
                            "from": "api_order","as": "orders", #,"localField": "id","foreignField": "campaign_id"
                            'let': {'id': "$id" },
                            "pipeline":[
                                {"$match":{
                                    '$expr': { '$eq': ["$$id", "$campaign_id"] },
                                    "id":{"$ne":None}}
                                 },
                                {"$project":{"_id":0,"id":1,"subtotal":1}},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"id":1,
                    "campaign_sales":{"$sum":"$orders.subtotal"},
                    "orders":1}}
                ]
            },
        },
        {"$project":{"_id":0,
        "average_sales":{"$avg":"$campaigns.campaign_sales"},
        # "campaigns":1
        }}
    ])
    l = list(cursor)
    return l[0].get('average_sales',0) if l else 0


def get_average_comment_count(user_subscription_id):
    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","as": "campaigns", #"localField": "id","foreignField": "user_subscription_id"
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$user_subscription_id"] },
                        "id":{"$ne":None}}
                     },
                    {
                        "$lookup": {
                            "from": "api_campaign_comment","as": "comments", # ,"localField": "id","foreignField": "campaign_id"
                            'let': {'id': "$id" },
                            "pipeline":[
                                {"$match":{
                                    '$expr': { '$eq': ["$$id", "$campaign_id"] },
                                    "id":{"$ne":None}}
                                 },
                                {"$project":{"_id":0,"id":1,"count":{"$sum":1}}},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"id":1,
                    "campaign_comments_count":{"$sum":"$comments.count"},
                    "orders":1}}
                ]
            },
        },
        {"$project":{"_id":0,
        "average_comment_count":{"$avg":"$campaigns.campaign_comments_count"},
        # "campaigns":1
        }}
    ])
    l = list(cursor)
    return l[0].get('average_comment_count',0) if l else 0