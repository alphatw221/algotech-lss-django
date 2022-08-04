from backend.pymongo.mongodb import db
import pandas as pd
from pandas import json_normalize
from datetime import datetime
import arrow
import json
import copy

class SalesReport:
    basic_info_keys = ['post_comment', 'no_of_items_sold', 'no_of_items_unsold', 'total_no_of_items', 
                   'total_inventories', 'total_no_of_orders', 'total_amount', 'average_order_value']
    order_analysis_keys = ['status', 'qty', 'percentage_of_qty', 'total', 'percentage_of_total']
    best_selling_items_top_10_keys = ['item', 'qty_for_sale', 'best_selling_status']
    
    data = []
    
    def __init__(self):
        pass
    
    @classmethod
    def normalize_start_time(cls, start_time):
        return arrow.get(start_time).replace(hour=0, minute=0, second=0).datetime
    
    @classmethod
    def normalize_end_time(cls, end_time):
        return arrow.get(end_time).replace(hour=23, minute=59, second=59).datetime
    
    @classmethod
    def get_basic_info(cls, start_time, end_time):
        query=db.api_campaign.aggregate([
            {
                "$match":{
                    "start_at":{
                        "$gte": start_time
                    },
                    "end_at": {
                        "$lte": end_time
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
                    "campaign_id":"$id",
                    "start_at": "$start_at",
                    "end_at": "$end_at",
                    "post_comment":{"$size":"$campaign_comment.id"},
                    "no_of_items_sold":{"$size": "$campaign_product_sold.id"},
                    "no_of_items_unsold":{"$size": "$campaign_product_unsold.id"},
                    "total_no_of_items":{"$size": "$campaign_product_total_item.id"},
                    "total_inventories":{"$sum": "$campaign_product_total_item.qty_for_sale"},
                    "total_no_of_orders": {"$add":[{"$size": "$pre_orders.id"},{"$size": "$orders.id"}]},
                    "total_amount": {"$add":[{"$sum": "$pre_orders.total"},{"$sum": "$orders.total"}]},
                    "average_order_value":{ "$divide": [{"$add":[{"$sum": "$pre_orders.total"},{"$sum": "$orders.total"}]}, 2 ] }
                }
            },
            { "$sort" : { "campaign_id" : 1 } }
        ])
        df = json_normalize(list(query))
        return df
    
    @classmethod
    def get_top_10_itmes(cls, start_time, end_time):
        query=db.api_campaign.aggregate([
            {
                "$match":{
                    "start_at":{
                        "$gte": start_time
                    },
                    "end_at": {
                        "$lte": end_time
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
                                "name":1,
                                "order_product_qty":{"$sum":"$order_product.qty"},
                                "qty_for_sale":1,
                                "status": {
                                    "$switch": {
                                      "branches": [
                                        {
                                          "case": {"$eq": ["$qty_for_sale", {"$sum":"$order_product.qty"}] },
                                          "then": "Sold Out"
                                        }
                                      ],
                                      "default": ""
                                    }

                                }
                            }
                        },
                        {"$sort": {"order_product_qty":-1}},
                        { "$limit": 10 }
                    ]
                },
            },
            {
                "$project":{
                    "_id":0,
                    "campaign_id":"$id",
                    "item": "$campaign_product.name",
                    "qty_for_sale": "$campaign_product.qty_for_sale",
#                     "order_product_qty": "$campaign_product.order_product_qty",
                    "best_selling_status": "$campaign_product.status"

                }
            },
            { "$sort" : { "campaign_id" : 1 } }

        ])
        df = json_normalize(list(query))
        return df
    @classmethod
    def get_order_data(cls, start_time, end_time):
    
        cursor=db.api_campaign.aggregate([
            {
                "$match":{
                    "start_at":{
                        "$gte": start_time
                    },
                    "end_at": {
                        "$lte": end_time
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
                        "id": "$data.campaign_id",
                        "status": "$data.new_type"
                    },
                    "campaign_id": {"$first": "$data.campaign_id"},
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

            { "$sort" : { "campaign_id" : 1 } }
        ])
        return list(cursor)
    @classmethod
    def modify_order_data(cls, report):
        def checkLack(x):
            if len(x) == 1 and x[0] == "paid":
                return "unpaid"
            elif len(x) == 1 and x[0] == "unpaid":
                return "paid"
            else:
                return ""
        def insert_0(x):
            cols = ['qty', 'total', 'percentage_of_qty', 'percentage_of_total']
            if x["lack"] == "paid":
                return [[0] + x[col] for col in cols]
            elif x["lack"] == "unpaid":
                return [x[col] + [0] for col in cols]
            else:
                return [x[col] for col in cols]

        df = json_normalize(report)
        df.loc[:,"new_status"] = df["status"].apply(lambda x: 'unpaid' if x in ['review', 'cart'] else 'paid')
        df = df.groupby(["campaign_id", "new_status"]).agg({'qty': 'sum', 'total': 'sum'}).reset_index()

        df = df.groupby(["campaign_id"]).agg({'new_status': list, 'qty': list, 'total':list}).reset_index()
        df.loc[:, "lack"] = df["new_status"].apply(checkLack)


        df.loc[:, "percentage_of_qty"] = df["qty"].apply(lambda x: [round(i/sum(x)*100,2) for i in x])
        df.loc[:, "percentage_of_total"] = df["total"].apply(lambda x: [round(i/sum(x)*100,2) for i in x])


        df["qty"], df["total"], df['percentage_of_qty'], df['percentage_of_total'] = zip(*df.apply(insert_0, axis=1))
        df.loc[:, "status"] = df.apply(lambda _: ["paid", "unpaid"], axis=1)
        df = df[["campaign_id", "status", "qty", "percentage_of_qty", "total", "percentage_of_total"]]
        return df
   
    @classmethod
    def get_order_analysis(cls, start_time, end_time):
        data = SalesReport.get_order_data(start_time, end_time)
        report = SalesReport.modify_order_data(data)
        return report
    
    @classmethod
    def merge_data(cls, basic_info, top_10_itmes, order_analysis):

        df = basic_info.merge(top_10_itmes, on="campaign_id", how="outer").merge(order_analysis, on="campaign_id", how="outer")
        result = df.to_json(orient="records")
        json_data = json.loads(result)
        
        campaign_template = {
            "campaign_id":"",
            "start_at": "",
            "end_at": "",
            "basic_info": {},
            "order_analysis": {},
            "best_selling_items_top_10": {}
        }

        for row in json_data:
            new_row_data = copy.deepcopy(row)
            new_data = copy.deepcopy(campaign_template)
            for key in new_data:
                if key == "basic_info":
                    for b_key in cls.basic_info_keys:
                        new_data[key][b_key] = new_row_data[b_key]
                elif key == "order_analysis":
                    for o_key in cls.order_analysis_keys:
                        new_data[key][o_key] = new_row_data[o_key]
                elif key == "best_selling_items_top_10":
                    for s_key in cls.best_selling_items_top_10_keys:
                        if s_key == "best_selling_status":
                            new_data[key]['status'] = new_row_data[s_key]
                        else:
                            new_data[key][s_key] = new_row_data[s_key]
                else:
                    new_data[key] = new_row_data[key]
            cls.data.append(new_data.copy())
        return cls.data
    
    @classmethod
    def reformat_data(cls, data):
        for campaign in data:
            for key in ['order_analysis', 'best_selling_items_top_10']:
                try:
                    new_format_df = pd.DataFrame(data=campaign[key])
                    new_format_json = new_format_df.to_json(orient="records")
                    campaign[key] = json.loads(new_format_json)
                except:
                    campaign[key] = {}
        return data