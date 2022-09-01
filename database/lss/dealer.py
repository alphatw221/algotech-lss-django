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