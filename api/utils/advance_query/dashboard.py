from backend.pymongo.mongodb import db
from datetime import datetime

def get_total_revenue(user_subscription_id):
    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","localField": "id","foreignField": "user_subscription_id","as": "campaigns",
                "pipeline":[
                    {"$match":{"id":{"$ne":None}}},
                    {
                        "$lookup": {
                            "from": "api_order","localField": "id","foreignField": "campaign_id","as": "orders",
                            "pipeline":[
                                {"$match":{"id":{"$ne":None}}},
                                {"$project":{"_id":0,"id":1,"total":1}},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"id":1,
                    "campaign_total":{"$sum":"$orders.total"},
                    "orders":1}}
                ]
            },
        },
        {"$project":{"_id":0,"id":1,
        "revenue_total":{"$sum":"$campaigns.campaign_total"},
        # "campaigns":1
        }}
    ])
    l = list(cursor)
    return l[0].get('revenue_total',0) if l else 0

def get_order_total_sales(user_subscription_id):
    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","localField": "id","foreignField": "user_subscription_id","as": "campaigns",
                "pipeline":[
                    {"$match":{"id":{"$ne":None}}},
                    {
                        "$lookup": {
                            "from": "api_order","localField": "id","foreignField": "campaign_id","as": "orders",
                            "pipeline":[
                                {"$match":{"id":{"$ne":None}}},
                                {
                                    "$lookup": {
                                        "from": "api_order_product","localField": "id","foreignField": "order_id","as": "order_products",
                                        "pipeline":[
                                            {"$match":{"id":{"$ne":None}}},
                                            {"$project":{"_id":0,"id":1,"qty":1}},
                                        ]
                                    },
                                },
                                {"$project":{"_id":0,"id":1,
                                "order_total":{"$sum":"$order_products.qty"},
                                "order_products":1
                                }},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"id":1,
                    "campaign_total":{"$sum":"$orders.order_total"},
                    "orders":1}}
                ]
            },
        },
        {"$project":{"_id":0,"id":1,
        "total":{"$sum":"$campaigns.campaign_total"},
        # "campaigns":1
        }}
    ])
    l = list(cursor)
    return l[0].get('total',0) if l else 0


def get_pre_order_total_sales(user_subscription_id):
    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","localField": "id","foreignField": "user_subscription_id","as": "campaigns",
                "pipeline":[
                    {"$match":{"id":{"$ne":None}}},
                    {
                        "$lookup": {
                            "from": "api_pre_order","localField": "id","foreignField": "campaign_id","as": "pre_orders",
                            "pipeline":[
                                {"$match":{"id":{"$ne":None}}},
                                {
                                    "$lookup": {
                                        "from": "api_order_product","localField": "id","foreignField": "order_id","as": "order_products",
                                        "pipeline":[
                                            {"$match":{"id":{"$ne":None}}},
                                            {"$project":{"_id":0,"id":1,"qty":1}},
                                        ]
                                    },
                                },
                                {"$project":{"_id":0,"id":1,
                                "order_total":{"$sum":"$order_products.qty"},
                                "order_products":1
                                }},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"id":1,
                    "campaign_total":{"$sum":"$pre_orders.order_total"},
                    "pre_orders":1}}
                ]
            },
        },
        {"$project":{"_id":0,"id":1,
        "total":{"$sum":"$campaigns.campaign_total"},
        # "campaigns":1
        }}
    ])
    l = list(cursor)
    return l[0].get('total',0) if l else 0


def get_order_total_sales_by_month(user_subscription_id):

    first_day_of_the_month = datetime.now().replace(day=1,hour=0,minute=0,second=0,microsecond=0)

    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","localField": "id","foreignField": "user_subscription_id","as": "campaigns",
                "pipeline":[
                    {"$match":{"id":{"$ne":None},"start_at":{"$gte":first_day_of_the_month}}},
                    {
                        "$lookup": {
                            "from": "api_order","localField": "id","foreignField": "campaign_id","as": "orders",
                            "pipeline":[
                                {"$match":{"id":{"$ne":None}}},
                                {
                                    "$lookup": {
                                        "from": "api_order_product","localField": "id","foreignField": "order_id","as": "order_products",
                                        "pipeline":[
                                            {"$match":{"id":{"$ne":None}}},
                                            {"$project":{"_id":0,"id":1,"qty":1}},
                                        ]
                                    },
                                },
                                {"$project":{"_id":0,"id":1,
                                "order_total":{"$sum":"$order_products.qty"},
                                "order_products":1
                                }},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"id":1,
                    "campaign_total":{"$sum":"$orders.order_total"},
                    "orders":1}}
                ]
            },
        },
        {"$project":{"_id":0,"id":1,
        "total":{"$sum":"$campaigns.campaign_total"},
        # "campaigns":1
        }}
    ])
    l = list(cursor)
    return l[0].get('total',0) if l else 0

def get_pre_order_total_sales_by_month(user_subscription_id):

    first_day_of_the_month = datetime.now().replace(day=1,hour=0,minute=0,second=0,microsecond=0)

    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","localField": "id","foreignField": "user_subscription_id","as": "campaigns",
                "pipeline":[
                    {"$match":{"id":{"$ne":None},"start_at":{"$gte":first_day_of_the_month}}},
                    {
                        "$lookup": {
                            "from": "api_pre_order","localField": "id","foreignField": "campaign_id","as": "pre_orders",
                            "pipeline":[
                                {"$match":{"id":{"$ne":None}}},
                                {
                                    "$lookup": {
                                        "from": "api_order_product","localField": "id","foreignField": "order_id","as": "order_products",
                                        "pipeline":[
                                            {"$match":{"id":{"$ne":None}}},
                                            {"$project":{"_id":0,"id":1,"qty":1}},
                                        ]
                                    },
                                },
                                {"$project":{"_id":0,"id":1,
                                "order_total":{"$sum":"$order_products.qty"},
                                "order_products":1
                                }},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"id":1,
                    "campaign_total":{"$sum":"$pre_orders.order_total"},
                    "pre_orders":1}}
                ]
            },
        },
        {"$project":{"_id":0,"id":1,
        "total":{"$sum":"$campaigns.campaign_total"},
        # "campaigns":1
        }}
    ])
    l = list(cursor)
    return l[0].get('total',0) if l else 0


def get_campaign_order_rank(user_subscription_id):

    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","localField": "id","foreignField": "user_subscription_id","as": "campaign_rank",
                "pipeline":[
                    {"$match":{"id":{"$ne":None}}},
                    {
                        "$lookup": {
                            "from": "api_order","localField": "id","foreignField": "campaign_id","as": "orders",
                            "pipeline":[
                                {"$match":{"id":{"$ne":None}}},
                                {"$project":{"_id":0,"count":{"$sum":1}}},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"title":1,
                    "order_count":{"$sum":"$orders.count"},
                    }},
                    { "$sort" : { "order_count" : -1 } }
                ]
            },
        },
        {"$project":{"_id":0,
        # "campaign_rank":1
        }}
    ])
    l = list(cursor)
    return l[0].get('campaign_rank',[]) if l else []

def get_campaign_comment_rank(user_subscription_id):

    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","localField": "id","foreignField": "user_subscription_id","as": "campaign_rank",
                "pipeline":[
                    {"$match":{"id":{"$ne":None}}},
                    {
                        "$lookup": {
                            "from": "api_campaign_comment","localField": "id","foreignField": "campaign_id","as": "comments",
                            "pipeline":[
                                {"$match":{"id":{"$ne":None}}},
                                {"$project":{"_id":0,"count":{"$sum":1}}},
                            ]
                        },
                    },
                    {"$project":{"_id":0,"title":1,
                    "comment_count":{"$sum":"$comments.count"},
                    }},
                    { "$sort" : { "comment_count" : -1 } }
                ]
            },
        },
        {"$project":{"_id":0,
        # "campaign_rank":1
        }}
    ])
    l = list(cursor)
    return l[0].get('campaign_rank',[]) if l else []