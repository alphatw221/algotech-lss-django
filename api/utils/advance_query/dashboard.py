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

def get_campaign_complete_sales(campaign_id):

    cursor=db.api_order.aggregate([
        {"$match":{"campaign_id":campaign_id,'status': 'complete'}},
        {
            "$group":
                {
                "_id":None,
                "campaign_sales": { "$sum": "$subtotal" },
                }
        },
        {"$project":{"_id":0,"campaign_sales":1}},
    ])

    l = list(cursor)
    return l[0].get('campaign_sales',0) if l else 0


def get_total_order_complete_proceed(user_subscription_id):

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
                                {"$project":{"_id":0,
                                "complete": {  "$cond": [ { "$eq": ["$status", "complete" ] }, 1, 0]},
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

def get_campaign_order_complete_proceed(campaign_id):

    cursor=db.api_campaign.aggregate([
        {"$match":{"id":campaign_id}},
        {
            "$lookup": {
                "from": "api_order","localField": "id","foreignField": "campaign_id","as": "orders",
                "pipeline":[
                    {"$match":{"id":{"$ne":None}}},
                    {"$project":{"_id":0,
                    "complete": {  "$cond": [ { "$eq": ["$status", "complete" ] }, 1, 0]},
                    "review": { "$cond": [ { "$eq": [ "$status", "review" ] }, 1, 0]}
                    }},
                ]
            },
        },
        {"$project":{"_id":0,
        "orders":1,
        "complete_count":{"$sum":"$orders.complete"},
        "review_count":{"$sum":"$orders.review"}
        }}
    ])
    l = list(cursor)
    return l[0].get('complete_count',0) if l else 0,\
        l[0].get('review_count',0) if l else 0


def get_total_pre_order_count(user_subscription_id):

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
                                {"$match":{"id":{"$ne":None},"subtotal":{"$ne":0}}},
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


def get_total_average_sales(user_subscription_id):
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


def get_total_average_comment_count(user_subscription_id):
    cursor=db.api_user_subscription.aggregate([
        {"$match":{"id":user_subscription_id}},
        {
            "$lookup": {
                "from": "api_campaign","localField": "id","foreignField": "user_subscription_id","as": "campaigns",
                "pipeline":[
                    {"$match":{"id":{"$ne":None}}},
                    {
                        "$lookup": {
                            "from": "api_campaign_comment","localField": "id","foreignField": "campaign_id","as": "comments",
                            "pipeline":[
                                {"$match":{"id":{"$ne":None}}},
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


def get_campaign_merge_order_list(campaign_id, search, page, page_size):


    if search:
        match_pipeline = {"$match":{"id":{"$ne":None}, "customer_name":{"$eq":search} }}
    else:
        match_pipeline = {"$match":{"id":{"$ne":None} }}

    if not page.isnumeric() or not page_size.isnumeric():
        return []
        
    page = int(page)
    page_size = int(page_size)

    cursor=db.api_campaign.aggregate([
        {"$match":{"id":campaign_id}},
        {
            "$lookup": {
                "from": "api_order","localField": "id","foreignField": "campaign_id","as": "orders",
                "pipeline":[
                    match_pipeline,
                    {"$addFields": { "type": "order","total_item": {"$size": { "$objectToArray": "$products"}}}},
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_pre_order","localField": "id","foreignField": "campaign_id","as": "pre_orders",
                "pipeline":[
                    match_pipeline,
                    {"$addFields": { "type": "pre_order","total_item": {"$size": { "$objectToArray": "$products"}}}},
                ]
            },
        },
        {"$project":{"_id":0,"data":{"$concatArrays":["$orders","$pre_orders"]}}},
        { "$unwind": "$data" },
        { "$sort" : { "data.created_at" : -1 } },
        {"$group":{
            "_id": {
                "id": "$data.id",
                "type": "$data.type"
            },
            "id":{"$first":"$data.id"},
            "platform":{"$first":"$data.platform"},
            "customer_name":{"$first":"$data.customer_name"},
            "customer_img":{"$first":"$data.customer_img"},
            "total_item":{"$first":"$data.total_item"},
            "subtotal":{"$first":"$data.subtotal"},
            "total":{"$first":"$data.total"},
            "payment_method":{"$first":"$data.payment_method"},
            "status":{"$first":"$data.status"},
            "type":{"$first":"$data.type"}
        }},
        {"$project":{"_id":0,}},
        { "$skip": (page-1)*page_size },
        { "$limit": page_size }

    ])
    l = list(cursor)
    # print(l)
    return l
