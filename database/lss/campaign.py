from numpy import array
from ._config import db
from ._config import Collection
from api import models

from bson.json_util import loads, dumps
from pprint import pprint

from datetime import datetime

__collection = db.api_campaign


class Campaign(Collection):

    _collection = db.api_campaign
    collection_name='api_campaign'
    template = models.campaign.campaign.api_campaign_template




def get_merge_order_list_pagination(campaign_id, search:str, status:str, filter_payment:list, filter_delivery:list, filter_platform:list, sort_by:dict, page:int=1, page_size:int=25):

    filter_query = {'$expr': { '$eq': ["$$id", "$campaign_id"] },"id":{"$ne":None} ,"products":{"$ne":{}}}

    if search not in ["",None,'undefined'] and search.isnumeric():
        filter_query["$or"]=[{"id":{"$eq":int(search)}}, {"customer_name":{"$regex":str(search),"$options": 'i'}}]
    elif search not in ["",None,'undefined']:
        filter_query["customer_name"]={"$regex":str(search),"$options": 'i'}
        
    if status == models.order.order.STATUS_REVIEW:
        filter_query['status']={"$in":[models.order.order.STATUS_REVIEW]} 
    elif status == models.order.order.STATUS_COMPLETE:
        filter_query['status']={"$in":[models.order.order.STATUS_COMPLETE,models.order.order.STATUS_SHIPPING_OUT]}
        
    if filter_payment not in [[],None]:
        filter_query['payment_method']={"$in": filter_payment}
        
    if filter_platform not in [[],None]:
        filter_query['platform']={"$in": filter_platform}
        
    if filter_delivery not in [[],None]:
        if filter_query.get('status',{}).get('$in'):
            filter_query['status']['$in']+=filter_delivery
        else:
            filter_query['status']={"$in": filter_delivery}
    
    sort_fields = {"id", "customer_name", "subtotal", "payment_method", "status"}
    if type(sort_by) != dict or not (sort_by.keys() & sort_fields):
        sort_by = { "created_at" : -1 }
    else:
        for key in list(sort_by.keys()):
            if key not in sort_fields:
                del sort_by[key]
                
    query = [
        {"$match":{"id":campaign_id}},
        {
            "$lookup": {
                "from": "api_order","as": "orders",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":filter_query},
                    {"$addFields": { "type": "order","total_item": {"$size": { "$objectToArray": "$products"}}}},
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_pre_order","as": "pre_orders",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":filter_query},
                    {"$addFields": { "type": "pre_order","total_item": {"$size": { "$objectToArray": "$products"}}}},
                ]
            },
        },
        {"$project":{"_id":0,"data":{"$concatArrays":["$orders","$pre_orders"]}} },
        { "$unwind": "$data" },
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
            "shipping_method":{"$first":"$data.shipping_method"},
            "meta":{"$first":"$data.meta"},
            "status":{"$first":"$data.status"},
            "type":{"$first":"$data.type"},
            "created_at":{"$first":"$data.created_at"}
        }},
        { "$sort" : sort_by},
        {"$project":{"_id":0,}},
    ]

    cursor=db.api_campaign.aggregate(query)

    skip = (page-1)*page_size
    
    bson = list(cursor)
    total_count = len(bson)
    bson = bson[skip:skip+page_size]
    data_str = dumps(bson)
    data_json = loads(data_str)    #TODO optimize # use skip limit  sum

    return data_json, total_count



def get_ongoing_campaign_disallow_overbook_campaign_product():
    cursor = __collection.aggregate([
        {'$match': {
            "start_at":{"$lt":datetime.utcnow()},
            "end_at":{"$gt":datetime.utcnow()}
        }},
        {'$lookup': {
            'from': 'api_campaign_product',
            'as': 'campaign_products',
            'let': { 'id': '$id' },
            'pipeline': [
                {'$match': {
                    '$expr': { '$eq': [ '$$id', '$campaign_id'] },
                    'overbook':False
                }},
                {"$project":{"_id":0,"id":1}}
            ]
        }},
        {"$project":{"_id":0,"campaign_products":1}},
        { "$unwind": "$campaign_products" },
        {"$project":{"id":"$campaign_products.id"}},
    ])

    l = list(cursor)
    return l








def get_order_complete_proceed_count(campaign_id):

    complete_status = [
        models.order.order.STATUS_COMPLETE
    ]
    proceed_status = [
        models.order.order.STATUS_PENDING ,
        models.order.order.STATUS_AWAITING_PAYMENT ,
        models.order.order.STATUS_AWAITING_FULFILLMENT ,
        models.order.order.STATUS_AWAITING_SHIPMENT ,
        models.order.order.STATUS_AWAITING_PICKUP ,
        models.order.order.STATUS_DISPUTED ,
        models.order.order.STATUS_PARTIALLY_REFUNDED ,
        models.order.order.STATUS_REFUNDED ,

    ]
    cursor=__collection.aggregate([
        {"$match":{"id":campaign_id}},
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
                    "complete": {  "$cond": [ { "$in":["$status", complete_status ] }, 1, 0]},
                    "proceed":{  "$cond": [ { "$in":["$status", proceed_status ] }, 1, 0]}
                    }},
                ]
            },
        },
        {"$project":{"_id":0,
        "orders":1,
        "complete_count":{"$sum":"$orders.complete"},
        "proceed_count":{"$sum":"$orders.proceed"}
        }}
    ])
    l = list(cursor)
    return l[0].get('complete_count',0) if l else 0,\
        l[0].get('proceed_count',0) if l else 0