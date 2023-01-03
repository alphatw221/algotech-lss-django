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

    def increment_silent_count(self, sync=False, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'silent_count': 1},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def reset_silent_count(self, sync=False, session=None):
        self._collection.update_one({'id':self.id},{"$set":{'silent_count': 0, 'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def deprioritize(self, sync=False, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'priority': 1},"$set":{'silent_count': 0, 'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)
    
    def reset_priority(self, sync=False, session=None):
        self._collection.update_one({'id':self.id},{"$set":{'silent_count': 0,'priority': 1, 'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

# def get_merge_order_list_pagination(campaign_id, search:str, status:str, filter_payment:list, filter_delivery:list, filter_platform:list, sort_by:dict, page:int=1, page_size:int=25):

#     filter_query = {'$expr': { '$eq': ["$$id", "$campaign_id"] },"id":{"$ne":None} ,"products":{"$ne":{}}}

#     if search not in ["",None,'undefined'] and search.isnumeric():
#         filter_query["$or"]=[{"id":{"$eq":int(search)}}, {"customer_name":{"$regex":str(search),"$options": 'i'}}]
#     elif search not in ["",None,'undefined']:
#         filter_query["customer_name"]={"$regex":str(search),"$options": 'i'}
        
#     if status == models.order.order.STATUS_REVIEW:
#         filter_query['status']={"$in":[models.order.order.STATUS_REVIEW]} 
#     elif status == models.order.order.STATUS_COMPLETE:
#         filter_query['status']={"$in":[models.order.order.STATUS_COMPLETE,models.order.order.STATUS_SHIPPING_OUT]}
        
#     if filter_payment not in [[],None]:
#         filter_query['payment_method']={"$in": filter_payment}
        
#     if filter_platform not in [[],None]:
#         filter_query['platform']={"$in": filter_platform}
        
#     if filter_delivery not in [[],None]:
#         if filter_query.get('status',{}).get('$in'):
#             filter_query['status']['$in']+=filter_delivery
#         else:
#             filter_query['status']={"$in": filter_delivery}
    
#     sort_fields = {"id", "customer_name", "subtotal", "payment_method", "status"}
#     if type(sort_by) != dict or not (sort_by.keys() & sort_fields):
#         sort_by = { "created_at" : -1 }
#     else:
#         for key in list(sort_by.keys()):
#             if key not in sort_fields:
#                 del sort_by[key]
                
#     query = [
#         {"$match":{"id":campaign_id}},
#         {
#             "$lookup": {
#                 "from": "api_order","as": "orders",
#                 'let': {'id': "$id" },
#                 "pipeline":[
#                     {"$match":filter_query},
#                     {"$addFields": { "type": "order","total_item": {"$size": { "$objectToArray": "$products"}}}},
#                 ]
#             },
#         },
#         {
#             "$lookup": {
#                 "from": "api_pre_order","as": "pre_orders",
#                 'let': {'id': "$id" },
#                 "pipeline":[
#                     {"$match":filter_query},
#                     {"$addFields": { "type": "pre_order","total_item": {"$size": { "$objectToArray": "$products"}}}},
#                 ]
#             },
#         },
#         {"$project":{"_id":0,"data":{"$concatArrays":["$orders","$pre_orders"]}} },
#         { "$unwind": "$data" },
#         {"$group":{
#             "_id": {
#                 "id": "$data.id",
#                 "type": "$data.type"
#             },
#             "id":{"$first":"$data.id"},
#             "platform":{"$first":"$data.platform"},
#             "customer_name":{"$first":"$data.customer_name"},
#             "customer_img":{"$first":"$data.customer_img"},
#             "total_item":{"$first":"$data.total_item"},
#             "subtotal":{"$first":"$data.subtotal"},
#             "total":{"$first":"$data.total"},
#             "payment_method":{"$first":"$data.payment_method"},
#             "shipping_method":{"$first":"$data.shipping_method"},
#             "meta":{"$first":"$data.meta"},
#             "status":{"$first":"$data.status"},
#             "type":{"$first":"$data.type"},
#             "created_at":{"$first":"$data.created_at"}
#         }},
#         { "$sort" : sort_by},
#         {"$project":{"_id":0,}},
#     ]

#     cursor=db.api_campaign.aggregate(query)

#     skip = (page-1)*page_size
    
#     bson = list(cursor)
#     total_count = len(bson)
#     bson = bson[skip:skip+page_size]
#     data_str = dumps(bson)
#     data_json = loads(data_str)    #TODO optimize # use skip limit  sum

#     return data_json, total_count



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

    if campaign_id:
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
                        "complete": {  "$cond": [ { "$eq":["$payment_status", models.order.order.PAYMENT_STATUS_PAID ] }, 1, 0]},
                        "proceed":{  "$cond": [ { "$ne":["$payment_status", models.order.order.PAYMENT_STATUS_PAID ] }, 1, 0]}
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
    return 0, 0
        
def sales_basic_info(start_time, end_time, user_subscription_id):
    query=db.api_campaign.aggregate([
        {
            "$match":{
                "start_at":{
                    "$gte": start_time
                },
                "end_at": {
                    "$lte": end_time
                },
                'user_subscription_id': {
                    "$eq": user_subscription_id
                }
            }
        },
        {
            "$lookup": {
                "from": "api_campaign_comment",
                "as": "campaign_comment",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$campaign_id"] },
                        "id":{"$ne":None}}
                    }
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_campaign_product",
                "as": "campaign_product_sold", 
                'let': {'id': "$id" },
                "pipeline":[
                    {
                        "$match":{
                            '$expr': { '$eq': ["$$id", "$campaign_id"] },
                            "id":{"$ne":None},
                            "qty_sold": {
                                "$gt": 0
                            }
                        }
                    }
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_campaign_product",
                "as": "campaign_product_unsold", 
                'let': {'id': "$id" },
                "pipeline":[
                    {
                        "$match":{
                            '$expr': { '$eq': ["$$id", "$campaign_id"] },
                            "id":{"$ne":None},
                            "qty_sold": {
                                "$eq": 0
                            }
                        }
                    }
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_campaign_product",
                "as": "campaign_product_total_item", 
                'let': {'id': "$id" },
                "pipeline":[
                    {
                        "$match":{
                            '$expr': { '$eq': ["$$id", "$campaign_id"] },
                            "id":{"$ne":None},
                        }
                    }
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_order",
                "as": "orders", 
                'let': {'id': "$id" },
                "pipeline":[
                    {
                        "$match":{
                            '$expr': { '$eq': ["$$id", "$campaign_id"] },
                            "id":{"$ne":None},
                        }
                    },
                    {
                        "$project":{
                            "_id":0,
                            "id":1,
                            "total":1
                        }
                    }
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_pre_order",
                "as": "pre_orders", 
                'let': {'id': "$id" },
                "pipeline":[
                    {
                        "$match":{
                            '$expr': { '$eq': ["$$id", "$campaign_id"] },
                            "id":{"$ne":None},
                            "subtotal":{"$gt":0},
                        }
                    },
                    {
                        "$project":{
                            "_id":0,
                            "id":1,
                            "total":1
                        }
                    }
                ]
            },
        },
        {
            "$project":{
                "_id":0,
                "post_comment":{"$size":"$campaign_comment.id"},
                "no_of_items_sold":{"$size": "$campaign_product_sold.id"},
                "no_of_items_unsold":{"$size": "$campaign_product_unsold.id"},
                "total_no_of_items":{"$size": "$campaign_product_total_item.id"},
                "total_inventories":{"$sum": "$campaign_product_total_item.qty_for_sale"},
                "total_no_of_orders": {"$add":[{"$size": "$pre_orders.id"},{"$size": "$orders.id"}]},
                "total_amount": {"$add":[{"$sum": "$pre_orders.total"},{"$sum": "$orders.total"}]},
            }
        },
        {
            "$project":{
                "post_comment":"$post_comment",
                "no_of_items_sold":"$no_of_items_sold",
                "no_of_items_unsold":"$no_of_items_unsold",
                "total_no_of_items":"$total_no_of_items",
                "total_inventories":"$total_inventories",
                "total_no_of_orders": "$total_no_of_orders",
                "total_amount": "$total_amount",
                "average_order_value":{ "$cond": [{ "$eq": [ "$total_no_of_orders", 0 ] }, 0, {"$round": [{"$divide":["$total_amount", "$total_no_of_orders"]}, 2]}] }
            }
        }
    ])
    return list(query)

def query_top_10_itmes_data(start_time, end_time, user_subscription_id):
    query=db.api_campaign.aggregate([
        {
            "$match":{
                "start_at":{
                    "$gte": start_time
                },
                "end_at": {
                    "$lte": end_time
                },
                'user_subscription_id': {
                    "$eq": user_subscription_id
                }
            }
        },
        {
            "$lookup": {
                "from": "api_campaign_product",
                "as": "campaign_product", 
                'let': {'id': "$id" },
                "pipeline":[
                    {
                        "$match":{
                            '$expr': { '$eq': ["$$id", "$campaign_id"] },
                            "id":{"$ne":None},
                        }
                    },
                    {
                        "$lookup": {
                            "from": "api_order_product",
                            "as": "order_product", 
                            'let': {'id': "$id" },
                            "pipeline":[
                                {
                                    "$match":{

                                        '$expr': {"$eq": ["$$id", "$campaign_product_id"]},
                                        "id":{"$ne":None},
                                    }
                                },
                                {
                                    "$project":{
                                        "_id":0,
                                        "qty":1,
                                    }
                                }
                            ]
                        },
                    },
                    {
                        "$project":{
                            "_id":0,
                            "campaign_id":1,
                            "name":1,
                            "order_product_qty":{"$sum":"$order_product.qty"},
                            "qty_for_sale":1,
                            "product_id": 1
                        }
                    },
                    
                ]
            },
        },
        {
            "$project":{
                "_id":0,
                "item": "$campaign_product.name",
                "qty_for_sale": "$campaign_product.qty_for_sale",
                "stock_product_id": "$campaign_product.product_id",
                "order_product_qty": "$campaign_product.order_product_qty",

            }
        },
        {"$sort": {"order_product_qty":-1}},
        { "$limit": 10 }

    ])
    return list(query)

def get_order_sales_data(start_time, end_time, user_subscription_id):

    cursor=db.api_campaign.aggregate([
        {
            "$match":{
                "start_at":{
                    "$gte": start_time
                },
                "end_at": {
                    "$lte": end_time
                },
                'user_subscription_id': {
                    "$eq": user_subscription_id
                }
            }
        },
        {
            "$lookup": {
                "from": "api_order",
                "as": "orders", 
                'let': {'id': "$id" },
                "pipeline":[
                    {
                        "$match":{
                            '$expr': { '$eq': ["$$id", "$campaign_id"] },
                            "id":{"$ne":None},
                        }
                    },
                    {"$addFields": { "new_type": "$status"}}
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_pre_order",
                "as": "pre_orders", 
                'let': {'id': "$id" },
                "pipeline":[
                    {
                        "$match":{
                            '$expr': { '$eq': ["$$id", "$campaign_id"] },
                            "id":{"$ne":None},
                            "subtotal": {"$ne" : 0}
                        }
                    },
                    {"$addFields": { "new_type": "cart"}}
                ]
            },
        },
        {"$project":{"_id":0,"data":{"$concatArrays":["$orders","$pre_orders"]}}},
        { "$unwind": "$data" },
        { "$group": {
                "_id": {
                    "status": "$data.new_type"
                },
                "status": {"$first": "$data.new_type"},
                "qty": {"$sum": 1},
                "total": {"$sum": "$data.total"}
            }
        },
        {
            "$project":{
                "_id":0,

            }
        },
    ])
    return list(cursor)

def get_previous_campaign_data(campaign_id, user_subscription_id):
    cursor = __collection.find({"user_subscription_id":user_subscription_id, "id":{"$lt":campaign_id}}).sort('id',-1).limit(1)
    l = list(cursor)
    return l[0] if len(l) else {}

def get_campaign_abandon_cart_which_enable_auto_clear(start_from=None, end_at=None):

    query = [
        {
            "$match":{
                # "$or":[
                #     {"start_at":{"$and":[{"$gt":start_from},{"$lt":end_at}]}},
                #     {"start_at":{"$lt":start_from}, "end_at":{"$gt":end_at}},
                #     {"end_at":{"$and":[{"$gt":start_from},{"$lt":end_at}]}},
                # ],
                "meta.enable_auto_clear" : True
            }
        },
        {
            "$project":{
                "_id" : 0,
                "id" : 1, 
                "allow_idle_period" : "$meta.allow_idle_period"
            }
        }
    ]
    cursor = __collection.aggregate(query)
    l = list(cursor)
    return l
