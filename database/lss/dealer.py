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
    