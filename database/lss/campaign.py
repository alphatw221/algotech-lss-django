from numpy import array
from ._config import db
from ._config import Collection
from api import models

from bson.json_util import loads, dumps
from pprint import pprint
__collection = db.api_campaign


class Campaign(Collection):

    _collection = db.api_campaign
    collection_name='api_campaign'





def get_merge_order_list_pagination(campaign_id, search:str, status:str, filter_payment:list, filter_delivery:list, filter_platform:list, page:int, page_size:int):

    # search and paginate by frontend by now
    if search not in ["",None,'undefined'] and search.isnumeric():
        match_pipeline_query = {"$match":{"$or":[{"id":{"$eq":int(search)}}, {"customer_name":{"$regex":str(search),"$options": 'i'}}] }}
    else:
        match_pipeline_query = {"$match":{"id":{"$ne":None} }}
    

    if status == models.order.order.STATUS_REVIEW:
        status_match_pipeline_query = {"$match":{"id":{"$ne":None},"status":{"$eq":models.order.order.STATUS_REVIEW} }}
    elif status == models.order.order.STATUS_COMPLETE:
        status_match_pipeline_query = {"$match":{"id":{"$ne":None},"status":{"$in":[models.order.order.STATUS_REVIEW,models.order.order.STATUS_SHIPPING_OUT]} }}
    else:
        status_match_pipeline_query = {"$match":{"id":{"$ne":None} }}
        
        
    if filter_payment not in [[],None]:
        filter_payment_query = {"$match":{"id":{"$ne":None},"payment_method":{"$in": filter_payment} }}
    else:
        filter_payment_query = {"$match":{"id":{"$ne":None} }}
        
    if filter_platform not in [[],None]:
        filter_platform_query = {"$match":{"id":{"$ne":None},"platform":{"$in": filter_platform} }}
    else:
        filter_platform_query = {"$match":{"id":{"$ne":None} }}
        
    if filter_delivery not in [[],None]:
        filter_delivery_query = {"$match":{"id":{"$ne":None},"status":{"$in": filter_delivery} }}
    else:
        filter_delivery_query = {"$match":{"id":{"$ne":None} }}


    count_query = [
        {"$match":{"id":campaign_id}},
        {
            "$lookup": {
                "from": "api_order","as": "orders",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$campaign_id"] },
                        "id":{"$ne":None} }
                    },
                    status_match_pipeline_query,
                    match_pipeline_query,
                    filter_payment_query,
                    filter_platform_query,
                    filter_delivery_query,
                    {"$project":{"_id":0, "count":{"$sum":1}}}
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_pre_order","as": "pre_orders",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$campaign_id"] },
                        "id":{"$ne":None} ,
                        "subtotal":{"$ne":0}}
                     },
                    status_match_pipeline_query,
                    match_pipeline_query,
                    filter_payment_query,
                    filter_platform_query,
                    filter_delivery_query,
                    {"$project":{"_id":0, "count":{"$sum":1}}}
                ]
            },
        },
        {"$project":{"_id":0, "id":1,"pre_orders":1, 'orders':1, "pre_order_count":{"$sum":"$pre_orders.count"},  "order_count":{"$sum":"$orders.count"}}}
    ]


    query = [
        {"$match":{"id":campaign_id}},
        {
            "$lookup": {
                "from": "api_order","as": "orders",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$campaign_id"] },
                        "id":{"$ne":None} }
                     },
                    {"$addFields": { "type": "order","total_item": {"$size": { "$objectToArray": "$products"}}}},
                ]
            },
        },
        {
            "$lookup": {
                "from": "api_pre_order","as": "pre_orders",
                'let': {'id': "$id" },
                "pipeline":[
                    {"$match":{
                        '$expr': { '$eq': ["$$id", "$campaign_id"] },
                        "id":{"$ne":None} ,
                        "subtotal":{"$ne":0}}
                     },
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
            "shipping_method":{"$first":"$data.shipping_method"},
            "meta":{"$first":"$data.meta"},
            "status":{"$first":"$data.status"},
            "type":{"$first":"$data.type"}
        }},
        {"$project":{"_id":0,}},
        status_match_pipeline_query,
        match_pipeline_query,
        filter_payment_query,
        filter_platform_query,
        filter_delivery_query,
        # { "$skip": (page-1)*page_size },    # search and paginate by frontend by now
        # { "$limit": page_size }
    ]
    page = int(page)
    page_size = int(page_size)

    count = db.api_campaign.aggregate(count_query)
    pprint(count)
    pprint(list(count))
    query.append({ "$skip": (page-1)*page_size })
    query.append({ "$limit": page_size })
    cursor=db.api_campaign.aggregate(query)
    l = list(cursor)

    merge_list_str = dumps(l)
    merge_list_json = loads(merge_list_str)


    return {'count':1,'data':merge_list_json}
