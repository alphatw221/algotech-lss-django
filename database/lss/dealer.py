from re import L
from backend.pymongo.mongodb import db
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def get_dealer_campaigns_info_analysis(user_subscription_id):
    cursor = db.api_user_subscription.aggregate([
        {'$match': {'dealer_id': user_subscription_id}},
        {'$project': { '_id': 0, 'id': 1, 'expired_at': 1 }},
        {'$lookup': {
            'from': 'api_campaign',
            'as': 'campaigns',
            'let': { 'id': '$id' },
            'pipeline': [
                {'$match': {
                    '$expr': { '$eq': [ '$$id', '$user_subscription_id'] },
                    'id': {'$ne': None}
                }},
                {'$lookup': {
                    'from': 'api_order',
                    'as': 'orders',
                    'let': { 'id': '$id' },
                    'pipeline': [
                        {'$match': {
                            '$expr': { '$eq': [ '$$id', '$campaign_id'] }
                        }},
                        {'$project': {'_id': 0, 'customer_id': 1, 'subtotal': 1}}
                    ]
                }},
                {'$project': {'_id': 0, 'orders': 1, 'orders_amount': {'$sum': '$orders.subtotal'}}},  ## orders subtotal amount
            ]
        }},
        {'$project': {
            'id': 1, 
            'campaigns': 1, 
            'almost_expired': {
                '$cond': [
                    {'$and': [
                            {'$lte': [datetime.now() + timedelta(days=30), '$expired_at']}, 
                            {'$gte': ['$expired_at', datetime.now()]}
                        ]
                    }, 1, 0 
                ]
            }, 
            'orders_amount': {'$sum': '$campaigns.orders_amount'}, 
            "campaigns_count": {'$size': '$campaigns'}
        }},
        {'$group': {
            '_id': '$id',
            'almost_expired': {'$first': '$almost_expired'},
            'orders_amount': {'$first': '$orders_amount'},
            'campaigns_count': {'$first': '$campaigns_count'},
            'customer_distinct': {'$addToSet': '$campaigns.orders.customer_id'}
        }},
        {'$unwind': "$customer_distinct"},
        {'$addFields': {
            'customer_id_list': {'$reduce': {
                'input': '$customer_distinct',
                'initialValue': [],
                'in': {'$concatArrays' : ["$$value", "$$this"]}
            }}
        }},
        {'$unwind': "$customer_id_list"},
        {'$group': {
            '_id': '$_id',
            'almost_expired': {'$first': '$almost_expired'},
            'customer_list': {'$addToSet': '$customer_id_list'},
            'orders_amount': {'$first': '$orders_amount'},
            'campaigns_count': {'$first': '$campaigns_count'}
        }},
        {'$group': {
            '_id': None,
            'almost_expired_count': {'$sum': '$almost_expired'},
            'orders_amount': {'$sum': '$orders_amount'},
            'campaigns_count': {'$sum': '$campaigns_count'},
            'customer_list': {'$addToSet': '$customer_list'}
        }},
        {'$addFields': {
            'unique_customer_list': {'$reduce': {
                'input': '$customer_list',
                'initialValue': [],
                'in': {'$concatArrays' : ["$$value", "$$this"]}
            }}
        }},
        {'$project': {'_id': 0, 'almost_expired_count': 1, 'orders_amount': 1, 'campaigns_count': 1, 'customers_count': {'$size': '$unique_customer_list'}}}
    ])

    l = list(cursor)
    return l


def get_dealer_members_growing(user_subscription_id, start_date, end_date):
    cursor = db.api_user_subscription.aggregate([
        {'$match': {
            '$and': [
                {'dealer_id': user_subscription_id},
                {'created_at': {'$gte': end_date, '$lte': start_date}}
            ]
        }},
        {'$group': {
            '_id': None,
            'subscriptions_list': {'$addToSet': '$id'}
        }},
        {'$project': {'_id': 0, 'subscription_count': {'$size': '$subscriptions_list'}}}
    ])

    l = list(cursor)
    return l


def get_dealer_period_revenue(user_subscription_id, start_date, end_date):
    cursor = db.api_user_subscription.aggregate([
        {'$match': {
            '$and': [
                {'dealer_id': user_subscription_id},
                {'started_at': {'$gte': end_date, '$lte': start_date}},
                {'type': {'$ne': 'dealer'}}
            ]
        }},
        {'$project': {
            '_id': 0, 
            'id': 1,
            'type': 1,
            'licence_period': {'$divide': [{'$subtract': ['$expired_at', '$started_at']}, 2592000000]}
        }},
        {'$group': {
            '_id': '$type',
            'id_list': {'$push': '$id'},
            'licence_count': {'$push': '$licence_period'},
            'count': {'$sum': 1}
        }}
    ])

    l = list(cursor)
    return l


def get_premium_period_order_count(user_subscription_id, start_date, end_date):
    cursor = db.api_campaign.aggregate([
        {'$match': {
            '$and': [
                {'user_subscription_id': user_subscription_id},
                {'created_at': {'$gte': end_date, '$lte': start_date}},
            ]
        }},
        {'$lookup': {
            'from': 'api_order',
            'as': 'orders',
            'let': { 'id': '$id' },
            'pipeline': [
                {'$match': {
                    '$expr': { '$eq': [ '$$id', '$campaign_id'] }
                }},
            ]
        }},
        {'$group': {
            '_id': None,
            'id_list': {'$addToSet': '$id'}
        }},
        {'$project': {'order_count': {'$size': '$id_list'}}}
    ])

    l = list(cursor)
    return l

def get_seller_info_from_dealer(dealer_id):
    filter_query = {'$expr': { '$eq': ["$$id", "$user_subscription_id"] },"id":{"$ne":None} }
    
    query = [
        {"$match":{"dealer_id":dealer_id}},
        {"$lookup":{
            "from": "api_user","as": "users",
            "localField": "id",
            "foreignField": "user_subscription_id",
            "pipeline":[
                {"$project":{
                    "_id":0,
                    "id":1,
                    "name":1,
                    "email":1,
                    "updated_at":1,
                    "phone":1,
                }}
            ],   
        }},
        {"$lookup":{
            "from": "api_campaign","as": "campaigns",
            "localField": "id",
            "foreignField": "user_subscription_id",
            "pipeline":[
                {"$lookup":{
                    "from":"api_order","as":"orders",
                    "localField": "id",
                    "foreignField": "campaign_id",
                    "pipeline":[
                        {'$match':{'status':{"$in":['complete','shipping out']}}},
                        {'$project': {'_id': 0,'customer_id': 1, 'subtotal': 1}}
                    ]
                }},
                {'$project': {'_id': 0, 'orders': 1, 'orders_amount': {'$sum': '$orders.subtotal'}}}
            ],   
        }},
        {'$project': {
            'id': 1, 
            'campaigns': 1, 
            'orders_amount': {'$sum': '$campaigns.orders_amount'}, 
            "campaigns_count": { "$size": "$campaigns" },
            'users':1,
            'name':1,
            'type':1,
            'started_at':1,
            'expired_at':1
            }},
        {'$group': {
            '_id': '$id',
            'users':{'$first':'$users'},
            'user_subscription_id':{'$first':'$id'},
            'user_subscription_name':{'$first':'$name'},
            'type':{'$first':'$type'},
            'plan_started_at':{'$first':'$started_at'},
            'plan_expired_at':{'$first':'$expired_at'},
            'orders_amount': {'$first': '$orders_amount'},
            'campaigns_count': {'$first': '$campaigns_count'},
            'customer_distinct': {'$addToSet': '$campaigns.orders.customer_id'}
        }},
        {'$unwind': "$customer_distinct"},
        {'$addFields': {
            'customer_id_list': {'$reduce': {
                'input': '$customer_distinct',
                'initialValue': [],
                'in': {'$concatArrays' : ["$$value", "$$this"]}
            }}
        }},
        {'$unwind': "$customer_id_list"},
        {'$group': {
            '_id': '$_id',
            'users':{'$first':'$users'},
            'user_subscription_id':{'$first':'$user_subscription_id'},
            'user_subscription_name':{'$first':'$user_subscription_name'},
            'type':{'$first':'$type'},
            'plan_started_at':{'$first':'$plan_started_at'},
            'plan_expired_at':{'$first':'$plan_expired_at'},
            'orders_amount': {'$first': '$orders_amount'},
            'campaigns_count': {'$first': '$campaigns_count'},
            'buyers': {'$addToSet': '$customer_id_list'}
        }},
        {'$project':{
            '_id':0,
            'users':1,
            'user_subscription_id':1,
            'user_subscription_name':1,
            'type':1,
            'plan_started_at':1,
            'plan_expired_at':1,
            'orders_amount':1,
            'campaigns_count':1,
            'buyers':{'$size':'$buyers'}
        }}
        
    ]
    
    cursor=db.api_user_subscription.aggregate(query)
    
    l = list(cursor)
    
    return l