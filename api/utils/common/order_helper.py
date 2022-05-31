from django.db.models.query import RawQuerySet
from pymongo import message
from requests.api import get
from api.utils.error_handle.error_handler.pymongo_error_handler import pymongo_error_handler
from api.utils.rule.check_rule.pre_order_check_rule import PreOrderCheckRule
from api.utils.rule.rule_checker.pre_order_rule_checker import PreOrderAddProductRuleChecker, PreOrderCheckoutRuleChecker, PreOrderDeleteProductRuleChecker, PreOrderUpdateProductRuleChecker
from backend.pymongo.mongodb import db, client, get_incremented_filed
from django.conf import settings
from datetime import datetime

from api.models.order.order import api_order_template
from api.models.order.order_product import api_order_product_template
from api.utils.common.verify import ApiVerifyError, platform_dict
from backend.cart.cart_product.request import RequestState
from api.utils.error_handle.error.pre_order_error import PreOrderErrors

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.error_handle.error_handler.add_or_update_by_comment_error_handler import add_or_update_by_comment_error_handler
from pymongo import errors as pymongo_errors

class PreOrderHelper():


    @classmethod
    @pymongo_error_handler
    def update_product(cls, api_user, pre_order, order_product, qty, lucky_draw_repeat=False):
        with client.start_session() as session:
            with session.start_transaction():
                api_pre_order = db.api_pre_order.find_one(
                    {"id": pre_order.id}, session=session)
                api_order_product = db.api_order_product.find_one(
                    {"id": order_product.id}, session=session)
                api_campaign_product = db.api_campaign_product.find_one(
                    {"id": api_order_product['campaign_product_id']}, session=session)

                ret = PreOrderUpdateProductRuleChecker.check(**{
                    'api_user':api_user,
                    'api_pre_order':api_pre_order,
                    'api_order_product':api_order_product,
                    'api_campaign_product':api_campaign_product,
                    'qty':qty,
                    'lucky_draw_repeat': lucky_draw_repeat
                    })

                qty = ret.get('qty')
                qty_difference = ret.get('qty_difference')

                db.api_campaign_product.update_one(
                    {'id': api_campaign_product['id']}, {"$inc": {'qty_sold': qty_difference}}, session=session)

                db.api_order_product.update_one(
                    {'id': api_order_product['id']}, {"$set": {'qty': qty, 'subtotal': float(qty*api_campaign_product["price"])}}, session=session)

                subtotal = api_pre_order['subtotal']+qty_difference*api_campaign_product['price']
                free_delivery = api_pre_order.get("free_delivery",False)
                shipping_cost = 0 if free_delivery else api_pre_order.get('shipping_cost',0)
                adjust_price = api_pre_order.get("adjust_price",0)
                total = subtotal+ float(shipping_cost)+float(adjust_price)

                db.api_pre_order.update_one(
                    {'id': pre_order.id},
                    {
                        "$set": {
                            "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
                            f"products.{str(api_campaign_product['id'])}.{'qty'}": qty,
                            f"products.{str(api_campaign_product['id'])}.{'subtotal'}": float(qty*api_order_product['price']),
                            "subtotal":subtotal,
                            "total":total
                        }
                    },session=session)
        return db.api_order_product.find_one({"id": api_order_product['id']}, {"_id": False})

    @classmethod
    @pymongo_error_handler
    def add_product(cls, api_user, pre_order, campaign_product, qty):
        with client.start_session() as session:
            with session.start_transaction():
                api_pre_order = db.api_pre_order.find_one(
                    {"id": pre_order.id}, session=session)
                api_campaign_product = db.api_campaign_product.find_one(
                    {"id": campaign_product.id}, session=session)

                ret = PreOrderAddProductRuleChecker.check(**{
                    'api_user':api_user,
                    'api_pre_order':api_pre_order,
                    'api_campaign_product':api_campaign_product,
                    'qty':qty,
                    })
                qty = ret.get('qty')
                qty_difference = ret.get('qty_difference')
                
                increment_id = get_incremented_filed(
                    collection_name='api_order_product', field_name='id', session=session)
                template = api_order_product_template.copy()
                template.update({
                    "id": increment_id,
                    "campaign_id": api_campaign_product["campaign_id"],
                    "campaign_product_id": api_campaign_product["id"],
                    "pre_order_id": api_pre_order["id"],
                    "qty": qty,
                    "customer_id": api_pre_order['customer_id'],
                    "customer_name": api_pre_order['customer_name'],
                    "platform": api_pre_order['platform'],
                    "type": api_campaign_product["type"],
                    "name": api_campaign_product["name"],
                    "price": api_campaign_product["price"],
                    "currency": api_campaign_product["currency"],
                    "currency_sign": api_campaign_product["currency_sign"],
                    "image": api_campaign_product["image"],
                    "subtotal": float(qty*api_campaign_product["price"])
                })
                db.api_order_product.insert_one(template, session=session)

                db.api_campaign_product.update_one({"id": campaign_product.id}, {
                                                "$inc": {'qty_sold': qty_difference}}, session=session)

                order_product = {
                    "order_product_id": increment_id,
                    "name": api_campaign_product["name"],
                    "image": api_campaign_product["image"],
                    "price": api_campaign_product["price"],
                    "type": api_campaign_product["type"],
                    "currency": api_campaign_product["currency"],
                    "currency_sign": api_campaign_product["currency_sign"],
                    "qty": qty,
                    "subtotal": float(qty*api_campaign_product["price"])
                }

                subtotal = api_pre_order['subtotal']+(qty_difference*api_campaign_product['price'])
                free_delivery = api_pre_order.get("free_delivery",False)
                shipping_cost = 0 if free_delivery else api_pre_order.get('shipping_cost',0)
                adjust_price = api_pre_order.get("adjust_price",0)
                total = subtotal+ float(shipping_cost)+float(adjust_price)

                db.api_pre_order.update_one(
                    {'id': pre_order.id},
                    {
                        "$set": {
                            "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
                            f"products.{str(api_campaign_product['id'])}": order_product,
                            "subtotal":subtotal,
                            "total":total
                        },
                    },session=session)
        return db.api_order_product.find_one({"id": increment_id}, {"_id": False})

    @classmethod
    @pymongo_error_handler
    def delete_product(cls, api_user, pre_order, order_product):
        with client.start_session() as session:
            with session.start_transaction():
                api_pre_order = db.api_pre_order.find_one(
                    {"id": pre_order.id}, session=session)
                api_order_product = db.api_order_product.find_one(
                    {"id": order_product.id}, session=session)

                campaign_product_id = api_order_product['campaign_product_id']
                api_campaign_product = db.api_campaign_product.find_one(
                    {"id": campaign_product_id}, session=session)


                PreOrderDeleteProductRuleChecker.check(**{
                    'api_user':api_user,
                    'api_pre_order':api_pre_order,
                    'api_order_product':api_order_product,
                    'api_campaign_product':api_campaign_product,
                    })

                if api_campaign_product:
                    db.api_campaign_product.update_one(
                        {'id': campaign_product_id}, {"$inc": {'qty_sold': -api_order_product['qty']}}, session=session)

                db.api_order_product.delete_one(
                    {'id': api_order_product['id']}, session=session)

                subtotal = api_pre_order['subtotal']-api_order_product['qty']*api_order_product['price']
                free_delivery = api_pre_order.get("free_delivery",False)
                shipping_cost = 0 if free_delivery else api_pre_order.get('shipping_cost',0)
                adjust_price = api_pre_order.get("adjust_price",0)
                total = subtotal+ float(shipping_cost)+float(adjust_price)

                db.api_pre_order.update_one(
                    {'id': pre_order.id},
                    {
                        "$unset":{
                            f"products.{str(campaign_product_id)}": "",
                        },
                        "$set": {
                            "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
                            
                            "subtotal":subtotal,
                            "total":total
                        },
                    },session=session)
        return True

    @classmethod
    @pymongo_error_handler
    def checkout(cls, api_user, pre_order):
        with client.start_session() as session:
            with session.start_transaction():
                api_pre_order = db.api_pre_order.find_one(
                    {"id": pre_order.id}, session=session)

                PreOrderCheckoutRuleChecker.check(**{
                    'api_user':api_user,
                    'pre_order':pre_order,
                    'api_pre_order':api_pre_order,
                    })

                # api_pre_order['total']=api_pre_order['subtotal']+api_pre_order['shipping_cost']+api_pre_order['adjust_price']

                increment_id = get_incremented_filed(
                    collection_name="api_order", field_name="id", session=session)
                api_order_data = api_pre_order.copy()

                del api_order_data['_id']
                api_order_data['id'] = increment_id
                api_order_data['created_at'] = datetime.utcnow()
                api_order_data['buyer_id'] = api_user.id
                template = api_order_template.copy()
                template.update(api_order_data)
                db.api_order.insert_one(template, session=session)

                db.api_order_product.update_many(
                    {"pre_order_id": api_pre_order["id"]}, {"$set": {"pre_order_id": None, "order_id": increment_id}})
                db.api_pre_order.update_one({"id": api_pre_order["id"]}, {
                                            "$set": {"products": {}, "total": 0, "subtotal": 0, "adjust_price":0, "adjust_title":"", "free_delivery":False, "history":{}, "meta":{}}}, session=session)
      
        return db.api_order.find_one({"id": increment_id}, {"_id": False})

    

    @classmethod
    @add_or_update_by_comment_error_handler
    def add_or_update_by_comment(cls, api_pre_order, api_campaign_product, qty):
        if not api_campaign_product['status']:
            return RequestState.INVALID_PRODUCT_NOT_ACTIVATED
        if api_campaign_product['max_order_amount'] and \
                qty > api_campaign_product['max_order_amount']:
            return RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT

        if str(api_campaign_product['id']) not in api_pre_order['products']:
            if qty > 0:
                cls.add_product_by_comment(
                        api_pre_order, api_campaign_product, qty)
                return RequestState.ADDED
            elif qty == 0:
                return RequestState.INVALID_ADD_ZERO_QTY
            else:
                return RequestState.INVALID_NEGATIVE_QTY

        else:
            if qty > 0:
                if not api_campaign_product['customer_editable']:
                    return RequestState.INVALID_EDIT_NOT_ALLOWED

                cls.update_product_by_comment(api_pre_order, api_campaign_product, qty)
                return RequestState.UPDATED
            elif qty == 0:
                if not api_campaign_product['customer_removable']:
                    return RequestState.INVALID_REMOVE_NOT_ALLOWED
                cls.delete_product_by_comment(
                        api_pre_order, api_campaign_product)
                return RequestState.DELETED
            else:
                return RequestState.INVALID_NEGATIVE_QTY


    @classmethod
    def add_product_by_comment(cls, api_pre_order, api_campaign_product, qty):
        with client.start_session() as session:
            with session.start_transaction():

                api_pre_order = db.api_pre_order.find_one({"id":api_pre_order['id']}, session=session)
                api_campaign_product = db.api_campaign_product.find_one({"id":api_campaign_product['id']}, session=session)

                ret = PreOrderCheckRule.is_stock_avaliable(**{'api_campaign_product':api_campaign_product,'qty':qty})
                qty_difference = ret.get('qty_difference')

                increment_id = get_incremented_filed(
                    collection_name="api_order_product", field_name="id", session=session)
                template = api_order_product_template.copy()
                template.update({
                    "id": increment_id,
                    "campaign_id": api_campaign_product["campaign_id"],
                    "campaign_product_id": api_campaign_product["id"],
                    "pre_order_id": api_pre_order["id"],
                    "qty": qty,
                    "customer_id": api_pre_order['customer_id'],
                    "customer_name": api_pre_order['customer_name'],
                    "platform": api_pre_order['platform'],
                    "type": api_campaign_product["type"],
                    "name": api_campaign_product["name"],
                    "price": api_campaign_product["price"],
                    "currency": api_campaign_product["currency"],
                    "currency_sign": api_campaign_product["currency_sign"],
                    "image": api_campaign_product["image"],
                    "subtotal": float(qty*api_campaign_product["price"])
                })
                db.api_order_product.insert_one(template, session=session)

                db.api_campaign_product.update_one({"id": api_campaign_product['id']}, {
                    "$inc": {'qty_sold': qty_difference}}, session=session)

                order_product = {
                    "order_product_id": increment_id,
                    "name": api_campaign_product["name"],
                    "image": api_campaign_product["image"],
                    "price": api_campaign_product["price"],
                    "type": api_campaign_product["type"],

                    "currency": api_campaign_product["currency"],
                    "currency_sign": api_campaign_product["currency_sign"],

                    "qty": qty,
                    "subtotal": float(qty*api_campaign_product["price"])
                }

                subtotal = api_pre_order['subtotal']+(qty_difference*api_campaign_product['price'])
                free_delivery = api_pre_order.get("free_delivery",False)
                shipping_cost = 0 if free_delivery else api_pre_order.get('shipping_cost',0)
                adjust_price = api_pre_order.get("adjust_price",0)
                total = subtotal+ float(shipping_cost)+float(adjust_price)

                db.api_pre_order.update_one(
                    {'id': api_pre_order['id']},
                    {
                        "$set": {
                            f"products.{str(api_campaign_product['id'])}": order_product,
                            "subtotal":subtotal,
                            "total":total
                        },
                    },session=session)

    @classmethod
    def update_product_by_comment(cls, api_pre_order, api_campaign_product, qty):

        with client.start_session() as session:
            with session.start_transaction():

                api_pre_order = db.api_pre_order.find_one({"id":api_pre_order['id']}, session=session)
                api_campaign_product = db.api_campaign_product.find_one({"id":api_campaign_product['id']}, session=session)

                api_order_product = db.api_order_product.find_one(
                    {"pre_order_id": api_pre_order['id'], "campaign_product_id": api_campaign_product['id']}, session=session)

                ret = PreOrderCheckRule.is_stock_avaliable(**{'api_campaign_product':api_campaign_product,'qty':qty,'api_order_product':api_order_product})
                qty_difference = ret.get('qty_difference')

                db.api_campaign_product.update_one(
                    {'id': api_campaign_product['id']}, {"$inc": {'qty_sold': qty_difference}}, session=session)

                db.api_order_product.update_one(
                    {'id': api_order_product['id']}, {"$set": {'qty': qty, 'subtotal': float(qty*api_campaign_product["price"])}}, session=session)

                subtotal = api_pre_order['subtotal']+qty_difference*api_campaign_product['price']
                free_delivery = api_pre_order.get("free_delivery",False)
                shipping_cost = 0 if free_delivery else api_pre_order.get('shipping_cost',0)
                adjust_price = api_pre_order.get("adjust_price",0)
                total = subtotal+ float(shipping_cost)+float(adjust_price)

                db.api_pre_order.update_one(
                    {'id': api_pre_order['id']},
                    {
                        "$set": {
                            f"products.{str(api_campaign_product['id'])}.{'qty'}": qty,
                            f"products.{str(api_campaign_product['id'])}.{'subtotal'}": float(qty*api_order_product['price']),
                            "subtotal":subtotal,
                            "total":total
                        },
                    },session=session)

    @classmethod
    def delete_product_by_comment(cls, api_pre_order, api_campaign_product):
        with client.start_session() as session:
            with session.start_transaction():

                api_pre_order = db.api_pre_order.find_one({"id":api_pre_order['id']}, session=session)
                api_campaign_product = db.api_campaign_product.find_one({"id":api_campaign_product['id']}, session=session)

                api_order_product = db.api_order_product.find_one(
                    {"pre_order_id": api_pre_order['id'], "campaign_product_id": api_campaign_product['id']}, session=session)

                db.api_campaign_product.update_one(
                    {'id': api_campaign_product['id']}, {"$inc": {'qty_sold': -api_order_product['qty']}}, session=session)

                db.api_order_product.delete_one(
                    {'id': api_order_product['id']}, session=session)

                subtotal = api_pre_order['subtotal']-api_order_product['qty']*api_order_product['price']
                free_delivery = api_pre_order.get("free_delivery",False)
                shipping_cost = 0 if free_delivery else api_pre_order.get('shipping_cost',0)
                adjust_price = api_pre_order.get("adjust_price",0)
                total = subtotal+ float(shipping_cost)+float(adjust_price)

                db.api_pre_order.update_one(
                    {'id': api_pre_order['id']},
                    {
                        "$unset":{
                            f"products.{str(api_campaign_product['id'])}":""
                        },
                        "$set": {
                            "subtotal": subtotal,
                            "total": total
                        }
                    },session=session)
    
    @classmethod
    def count_buyer_pre_order_detail(cls, pre_order, campaign, pre_order_data=None):
        delivery_charge = float(campaign.meta_logistic.get('delivery_charge',0))

        if pre_order_data and pre_order_data.get('shipping_method') == 'in_store':
            delivery_charge=0
        else:
            delivery_titles = campaign.meta_logistic.get('additional_delivery_charge_title')
            delivery_types = campaign.meta_logistic.get('additional_delivery_charge_type')
            delivery_prices = campaign.meta_logistic.get('additional_delivery_charge_price')
            shipping_option = None if not pre_order_data else pre_order_data.get('shipping_option') 

            if (shipping_option and delivery_titles and delivery_types and delivery_prices and shipping_option):
                addition_delivery_index = delivery_titles.index(shipping_option)

                if delivery_types[addition_delivery_index] == '+':
                    delivery_charge += float(delivery_prices[addition_delivery_index]) 

                elif delivery_types[addition_delivery_index] == '=':
                    delivery_charge =  float(delivery_prices[addition_delivery_index])

            free_delivery_for_order_above_price = campaign.meta_logistic.get('free_delivery_for_order_above_price') if campaign.meta_logistic.get('is_free_delivery_for_order_above_price') == 1 else 0
            free_delivery_for_how_many_order_minimum = campaign.meta_logistic.get('free_delivery_for_how_many_order_minimum') if campaign.meta_logistic.get('is_free_delivery_for_how_many_order_minimum') == 1 else 0
            
            is_subtotal_over_free_delivery_threshold = pre_order.subtotal >= float(free_delivery_for_order_above_price)
            is_items_over_free_delivery_threshold = len(pre_order.products) >= float(free_delivery_for_how_many_order_minimum)

            if pre_order.free_delivery :
                delivery_charge = 0
            if is_subtotal_over_free_delivery_threshold:
                delivery_charge = 0
                if pre_order_data:
                    pre_order_data['meta']['subtotal_over_free_delivery_threshold'] = True
            if is_items_over_free_delivery_threshold:
                delivery_charge = 0
                if pre_order_data:
                    pre_order_data['meta']['items_over_free_delivery_threshold'] = True
        if pre_order_data:
            pre_order_data['total'] = pre_order.subtotal + pre_order.adjust_price + delivery_charge

        pre_order_price_information = {
            'pre_order_data': pre_order_data,
            'subtotal': pre_order.subtotal,
            'adjust_price': pre_order.adjust_price,
            'delivery_charge': delivery_charge,
            'total': pre_order.subtotal + pre_order.adjust_price + delivery_charge
        }

        return pre_order_price_information


class OrderHelper():

    class OrderValidator():
        pass

    @classmethod
    @api_error_handler
    def cancel(self, api_user, order):
        with client.start_session() as session:
            with session.start_transaction():
                api_order = db.api_order.find_one(
                    {'id': order.id}, session=session)
                campaign_id = api_order['campaign_id']
                customer_id = api_order['customer_id']
                pre_order_id = db.api_pre_order.find_one(
                    {'campaign_id': campaign_id, 'customer_id': customer_id})['id']
                products_dict = {}
                total_count = 0

                order_products = db.api_order_product.find(
                    {'campaign_id': campaign_id, 'customer_id': customer_id, 'order_id': order.id})
                for order_product in order_products:
                    campaign_product_id = order_product['campaign_product_id']
                    price = db.api_campaign_product.find_one(
                        {'id': campaign_product_id})['price']
                    product_dict = {}

                    if db.api_order_product.find({'order_id': None, 'campaign_id': campaign_id, 'campaign_product_id': campaign_product_id, "customer_id": customer_id}).count() > 0:
                        pre_order_product = db.api_order_product.find(
                            {'order_id': None, 'campaign_id': campaign_id, 'campaign_product_id': campaign_product_id, "customer_id": customer_id})
                        db.api_order_product.update_one(
                            {'pre_order_id': pre_order_id,
                                'campaign_product_id': campaign_product_id},
                            {'$set':
                                {'qty': order_product['qty'] +
                                    pre_order_product['qty']}
                             }
                        )
                        db.api_order_product.delete_one(
                            {'order_id': order.id, 'campaign_product_id': campaign_product_id})
                        product_key = ['order_product_id', 'name', 'image', 'price',
                                       'type', 'currency', 'currency_sign', 'qty', 'subtotal']
                        product_val = [pre_order_product['id'], pre_order_product['name'], pre_order_product['image'], pre_order_product['price'], pre_order_product['type'],
                                       pre_order_product['currency'], pre_order_product['currency_sign'], order_product['qty'] + pre_order_product['qty'], order_product['subtotal'] + pre_order_product['subtotal']]
                        product_dict = dict(zip(product_key, product_val))
                        total_count += (order_product['qty'] +
                                        pre_order_product['qty']) * price
                    else:
                        db.api_order_product.update_one(
                            {'order_id': order.id,
                                'campaign_product_id': campaign_product_id},
                            {'$set':
                                {'pre_order_id': pre_order_id, 'order_id': None}
                             }
                        )
                        product_key = ['order_product_id', 'name', 'image', 'price',
                                       'type', 'currency', 'currency_sign', 'qty', 'subtotal']
                        product_val = [order_product['id'], order_product['name'], order_product['image'], order_product['price'], order_product['type'],
                                       order_product['currency'], order_product['currency_sign'], order_product['qty'], order_product['subtotal']]
                        product_dict = dict(zip(product_key, product_val))
                        total_count += order_product['qty'] * price
                    products_dict[str(campaign_product_id)] = product_dict

                pre_order_key = ['shipping_first_name', 'shipping_last_name', 'shipping_email', 'shipping_phone', 'shipping_address_1',
                                 'shipping_location', 'shipping_region', 'shipping_postcode', 'shipping_cost', 'products', 'subtotal']
                pre_order_val = ['', '', '', '', '', '',
                                 '', '', 0, products_dict, total_count]
                pre_order_dict = dict(zip(pre_order_key, pre_order_val))
                db.api_pre_order.update_one(
                    {'id': pre_order_id},
                    {'$set': pre_order_dict}
                )
                db.api_order.delete_one({'id': order.id})
        return pre_order_id

    @classmethod
    @api_error_handler
    def delete(self, api_user, order):
        with client.start_session() as session:
            with session.start_transaction():
                api_order = db.api_order.find_one(
                    {'id': order.id}, session=session)

                campaign_id = api_order['campaign_id']
                customer_id = api_order['customer_id']
                order_id = order.id

                order_products = db.api_order_product.find(
                    {'campaign_id': campaign_id, 'customer_id': customer_id, 'order_id': order_id})
                for order_product in order_products:
                    campaign_product_id = order_product['campaign_product_id']
                    order_qty = order_product['qty']

                    cp_product = db.api_campaign_product.find_one(
                        {'campaign_id': campaign_id, 'id': campaign_product_id})
                    db.api_campaign_product.update_one(
                        {'campaign_id': campaign_id, 'id': campaign_product_id},
                        {'$set':
                            {'qty_sold': cp_product['qty_sold'] - order_qty}
                         }
                    )
                    db.api_order_product.delete_one(
                        {'order_id': order_id, 'campaign_product_id': campaign_product_id})

                db.api_order.delete_one({'id': order_id})
