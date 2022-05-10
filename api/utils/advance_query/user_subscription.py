from backend.pymongo.mongodb import db


def get_user_subscription_buyer_list(user_subscription_id):
    cursor = db.api_user_subscription.aggregate([
        {'$match': {'id': user_subscription_id}},
        {'$lookup': {
            'from': 'api_campaign',
            'as': 'campaigns',
            'let': { 'id': '$id' },
            'pipeline': [
                {'$match': {
                    '$expr': { '$eq': [ '$$id', '$user_subscription_id' ] },
                    'id': {'$ne': None}
                }},
                {'$project': { '_id': 0, 'id': 1 }},
                {'$lookup': {
                    'from': 'api_order',
                    'as': 'orders',
                    'let': { 'id': '$id' },
                    'pipeline': [
                        {'$match': {
                            '$expr': { '$eq': [ '$$id', '$campaign_id'] }
                        }}
                    ],
                }},
                {'$unwind': '$orders'},  
                {'$match': {'orders': {'$ne': []}}},
                {'$project': {'_id': 0, 'orders': 1}},
            ]
        }},
        {'$unwind': '$campaigns'},  
        {'$project': { '_id': 0, 'campaigns': 1 }},
        {'$group': {
            '_id': '$campaigns.orders.customer_id',
            'customer_id': { '$first': '$campaigns.orders.customer_id'},
            'customer_name': { '$first': '$campaigns.orders.customer_name'},
            'customer_img': { '$first': '$campaigns.orders.customer_img'},
            'shipping_email': { '$first': '$campaigns.orders.shipping_email'},
            'shipping_phone': { '$first': '$campaigns.orders.shipping_phone'},
            'platform': { '$first': '$campaigns.orders.platform'},
        }},
    ])
    l = list(cursor)

    return l