from backend.pymongo.mongodb import db


def get_dealer_campaigns_info_analysis(user_subscription_id):
    cursor = db.api_user_subscription.aggregate([
        {'$match': {'dealer_id': user_subscription_id}},
        {'$project': { '_id': 0, 'id': 1 }},
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
        {'$project': {'id': 1, 'campaigns': 1, 'orders_amount': {'$sum': '$campaigns.orders_amount'}, "campaigns_count": { '$size': '$campaigns' }}},
        {'$group': {
            '_id': '$id',
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
            'customer_list': {'$addToSet': '$customer_id_list'},
            'orders_amount': {'$first': '$orders_amount'},
            'campaigns_count': {'$first': '$campaigns_count'}
        }},
        {'$group': {
            '_id': None,
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
        {'$project': {'_id': 1, 'orders_amount': 1, 'campaigns_count': 1, 'customers_count': {'$size': '$unique_customer_list'}}}
    ])

    l = list(cursor)
    return l