from django.db.models.query import RawQuerySet
from pymongo import message
from requests.api import get
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
    def update_product(cls, api_user, pre_order, order_product, campaign_product, qty):
        with client.start_session() as session:
            try:
                with session.start_transaction():
                    api_pre_order = db.api_pre_order.find_one(
                        {"id": pre_order.id}, session=session)
                    api_order_product = db.api_order_product.find_one(
                        {"id": order_product.id}, session=session)
                    api_campaign_product = db.api_campaign_product.find_one(
                        {"id": campaign_product.id}, session=session)

                    cls._check_lock(api_user, api_pre_order)
                    qty = cls._check_qty(api_campaign_product, qty)
                    cls._check_type(api_campaign_product)
                    cls._check_editable(api_user,api_campaign_product)

                    qty_difference = cls._check_stock(
                        api_campaign_product, original_qty=api_order_product['qty'], request_qty=qty)

                    db.api_campaign_product.update_one(
                        {'id': api_campaign_product['id']}, {"$inc": {'qty_sold': qty_difference}}, session=session)

                    db.api_order_product.update_one(
                        {'id': api_order_product['id']}, {"$set": {'qty': qty, 'subtotal': float(qty*api_campaign_product["price"])}}, session=session)

                    products = api_pre_order['products']
                    products[str(api_campaign_product['id'])]['qty'] = qty
                    products[str(api_campaign_product['id'])]['subtotal'] = float(
                        qty*api_order_product['price'])
                    print(qty_difference*api_campaign_product['price'])
                    db.api_pre_order.update_one(
                        {'id': pre_order.id},
                        {
                            "$set": {
                                "lock_at": datetime.now(), # if api_user and api_user.type == 'customer' else None,
                                "products": products
                            },
                            "$inc": {
                                "subtotal": qty_difference*api_campaign_product['price'],
                            }
                        },
                        session=session)
            except pymongo_errors.PyMongoError as e:
                print(e)
                raise pymongo_errors.PyMongoError("server busy, please try again later")
        return db.api_order_product.find_one({"id": api_order_product['id']}, {"_id": False})

    @classmethod
    def add_product(cls, api_user, pre_order, campaign_product, qty):
        with client.start_session() as session:
            try:
                with session.start_transaction():
                    api_pre_order = db.api_pre_order.find_one(
                        {"id": pre_order.id}, session=session)
                    api_campaign_product = db.api_campaign_product.find_one(
                        {"id": campaign_product.id}, session=session)

                    cls._check_lock(api_user, api_pre_order)
                    qty = cls._check_qty(api_campaign_product, qty)
                    cls._check_addable(api_pre_order, api_campaign_product)
                    cls._check_type(api_campaign_product)
                    qty_difference = cls._check_stock(
                        api_campaign_product, original_qty=0, request_qty=qty)

                    increment_id = get_incremented_filed(
                        collection_name='api_order_product', field_name='id')
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
                                                    "$inc": {'qty_sold': qty_difference}})

                    products = api_pre_order['products']
                    products[str(api_campaign_product['id'])] = {
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
                    db.api_pre_order.update_one(
                        {'id': pre_order.id},
                        {
                            "$set": {
                                "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
                                "products": products
                            },
                            "$inc": {
                                "subtotal": qty_difference*api_campaign_product['price'],
                            }
                        },
                        session=session)
            except pymongo_errors.PyMongoError as e:
                print(e)
                raise pymongo_errors.PyMongoError("server busy, please try again later")
        return db.api_order_product.find_one({"id": increment_id}, {"_id": False})

    @classmethod
    def delete_product(cls, api_user, pre_order, order_product, campaign_product):
        with client.start_session() as session:
            try:
                with session.start_transaction():
                    api_pre_order = db.api_pre_order.find_one(
                        {"id": pre_order.id}, session=session)
                    api_order_product = db.api_order_product.find_one(
                        {"id": order_product.id}, session=session)
                    api_campaign_product = db.api_campaign_product.find_one(
                        {"id": campaign_product.id}, session=session)

                    cls._check_lock(api_user, api_pre_order)
                    cls._check_removeable(api_user, api_campaign_product)

                    db.api_campaign_product.update_one(
                        {'id': api_campaign_product['id']}, {"$inc": {'qty_sold': -api_order_product['qty']}}, session=session)

                    db.api_order_product.delete_one(
                        {'id': api_order_product['id']}, session=session)

                    products = api_pre_order['products']
                    del products[str(api_campaign_product['id'])]
                    db.api_pre_order.update_one(
                        {'id': pre_order.id},
                        {
                            "$set": {
                                "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
                                "products": products
                            },
                            "$inc": {
                                "subtotal": -api_order_product['qty']*api_order_product['price'],
                            }
                        },
                        session=session)
            except pymongo_errors.PyMongoError as e:
                print(e)
                raise pymongo_errors.PyMongoError("server busy, please try again later")
        return True

    @classmethod
    def checkout(cls, api_user, pre_order):
        with client.start_session() as session:
            try:
                with session.start_transaction():
                    api_pre_order = db.api_pre_order.find_one(
                        {"id": pre_order.id}, session=session)

                    cls._check_allow_checkout(api_user, pre_order.campaign)
                    cls._check_lock(api_user, api_pre_order)
                    cls._check_empty(api_pre_order)

                    api_pre_order['total']=api_pre_order['subtotal']+api_pre_order['shipping_cost']+api_pre_order['adjust_price']

                    increment_id = get_incremented_filed(
                        collection_name="api_order", field_name="id")
                    api_order_data = api_pre_order.copy()
                    api_order_data['id'] = increment_id
                    del api_order_data['_id']
                    api_order_data['created_at'] = datetime.utcnow()
                    api_order_data['buyer_id'] = api_user.id
                    template = api_order_template.copy()
                    template.update(api_order_data)
                    #TODO add api_user reference
                    db.api_order.insert_one(template, session=session)

                    db.api_order_product.update_many(
                        {"pre_order_id": api_pre_order["id"]}, {"$set": {"pre_order_id": None, "order_id": increment_id}})
                    db.api_pre_order.update_one({"id": api_pre_order["id"]}, {
                                                "$set": {"products": {}, "total": 0, "subtotal": 0, "adjust_price":0, "adjust_title":"", "free_delivery":False, "history":{}}}, session=session)
            except pymongo_errors.PyMongoError as e:
                print(e)
                raise pymongo_errors.PyMongoError("server busy, please try again later")
        return db.api_order.find_one({"id": increment_id}, {"_id": False})

    @staticmethod
    def _check_platform(platform, customer_id, customer_name):
        pass

    @staticmethod
    def _check_lock(api_user, api_pre_order):
        return
        #2022.02.25 deactivated due to demo
        if not api_user:
            return
        if api_user.type == 'customer':
            return
        if api_pre_order['lock_at'] and datetime.timestamp(api_pre_order['lock_at'])+settings.CART_LOCK_INTERVAL > datetime.timestamp(datetime.now()):
            raise PreOrderErrors.PreOrderException('cart in use')

    @staticmethod
    def _check_qty(api_campaign_product, qty):
        if not qty:
            raise PreOrderErrors.PreOrderException('please enter qty')
        qty = int(qty)
        if not qty:
            raise PreOrderErrors.PreOrderException(
                'qty can not be zero or negitive')
        return qty

    @staticmethod
    def _check_stock(api_campaign_product, original_qty, request_qty):
        qty_difference = int(request_qty)-original_qty
        if qty_difference and api_campaign_product["qty_for_sale"]-api_campaign_product["qty_sold"] < qty_difference:
            raise PreOrderErrors.UnderStock("out of stock")
        return qty_difference

    @staticmethod
    def _check_removeable(api_user, api_campaign_product):
        if not api_user:
            return
        if api_user.type=="user":
            return
        if not api_campaign_product['customer_removable']:
            raise PreOrderErrors.RemoveNotAllowed("not removable")

    @staticmethod
    def _check_editable(api_user, api_campaign_product):
        if not api_user:
            return
        if api_user.type=="user":
            return
        if not api_campaign_product.get('customer_editable',False):
            raise PreOrderErrors.EditNotAllowed("not editable")


    @staticmethod
    def _check_addable(api_pre_order, api_campaign_product):
        if str(api_campaign_product["id"]) in api_pre_order["products"]:
            raise PreOrderErrors.PreOrderException(
                "product already in pre_order")

    @staticmethod
    def _check_empty(api_pre_order):
        if not bool(api_pre_order['products']):
            raise PreOrderErrors.PreOrderException('cart is empty')

    @staticmethod
    def _check_allow_checkout(api_user, campaign):
        if api_user and api_user.type=="user":
            return
        if not campaign.meta.get('allow_checkout', 1):
            raise PreOrderErrors.PreOrderException('check out not allow')

    @staticmethod
    def _check_type(api_campaign_product):
        if api_campaign_product['type'] == 'lucky_draw' or api_campaign_product['type'] == 'lucky_draw-fast':
            api_campaign_product['price'] = 0
        elif api_campaign_product['type'] == 'n/a':
            raise PreOrderErrors.UnderStock('out of stock')

    @classmethod
    @add_or_update_by_comment_error_handler
    def add_or_update_by_comment(cls, api_pre_order, api_campaign_product, qty):
        # try:
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
                # return None
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
                # return None
            elif qty == 0:
                if not api_campaign_product['customer_removable']:
                    return RequestState.INVALID_REMOVE_NOT_ALLOWED
                # delete
                cls.delete_product_by_comment(
                        api_pre_order, api_campaign_product)
                return RequestState.DELETED
                # return None
            else:
                return RequestState.INVALID_NEGATIVE_QTY

        # except PreOrderErrors.PreOrderException as e:
        #     return e.state

    @classmethod
    # @api_error_handler
    def add_product_by_comment(cls, api_pre_order, api_campaign_product, qty):
        with client.start_session() as session:
            # try:
            with session.start_transaction():
                qty_difference = cls._check_stock(
                    api_campaign_product, original_qty=0, request_qty=qty)

                increment_id = get_incremented_filed(
                    collection_name="api_order_product", field_name="id")
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
                    "$inc": {'qty_sold': qty_difference}})

                products = api_pre_order['products']

                products[str(api_campaign_product['id'])] = {
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

                db.api_pre_order.update_one(
                    {'id': api_pre_order['id']},
                    {
                        "$set": {
                            "products": products
                        },
                        "$inc": {
                            "subtotal": qty_difference*api_campaign_product['price'],
                        }
                    },
                    session=session)
                # return True
            # except pymongo_errors.PyMongoError as e:
            #     print(e)
            #     print('pymongo error!!!!')
            #     return False

    @classmethod
    # @api_error_handler
    def update_product_by_comment(cls, api_pre_order, api_campaign_product, qty):

        with client.start_session() as session:
            # try:
            with session.start_transaction():
                api_order_product = db.api_order_product.find_one(
                    {"pre_order_id": api_pre_order['id'], "campaign_product_id": api_campaign_product['id']}, session=session)

                qty_difference = cls._check_stock(
                    api_campaign_product, original_qty=api_order_product['qty'], request_qty=qty)

                db.api_campaign_product.update_one(
                    {'id': api_campaign_product['id']}, {"$inc": {'qty_sold': qty_difference}}, session=session)

                db.api_order_product.update_one(
                    {'id': api_order_product['id']}, {"$set": {'qty': qty, 'subtotal': float(qty*api_campaign_product["price"])}}, session=session)

                products = api_pre_order['products']
                products[str(api_campaign_product['id'])
                            ]['qty'] = qty
                products[str(api_campaign_product['id'])]['subtotal'] = float(
                    qty*api_order_product['price'])
                db.api_pre_order.update_one(
                    {'id': api_pre_order['id']},
                    {
                        "$set": {
                            "products": products
                        },
                        "$inc": {
                            "subtotal": qty_difference*api_campaign_product['price'],
                        }
                    },
                    session=session)
                # return True
            # except pymongo_errors.PyMongoError as e:
            #     print(e)
            #     print('pymongo error!!!!')
            #     return False

    @classmethod
    # @api_error_handler
    def delete_product_by_comment(cls, api_pre_order, api_campaign_product):
        with client.start_session() as session:
            # try:
            with session.start_transaction():
                api_order_product = db.api_order_product.find_one(
                    {"pre_order_id": api_pre_order['id'], "campaign_product_id": api_campaign_product['id']}, session=session)

                db.api_campaign_product.update_one(
                    {'id': api_campaign_product['id']}, {"$inc": {'qty_sold': -api_order_product['qty']}}, session=session)

                db.api_order_product.delete_one(
                    {'id': api_order_product['id']}, session=session)

                products = api_pre_order['products']
                del products[str(api_campaign_product['id'])]
                db.api_pre_order.update_one(
                    {'id': api_pre_order['id']},
                    {
                        "$set": {
                            "products": products
                        },
                        "$inc": {
                            "subtotal": -api_order_product['qty']*api_order_product['price'],
                        }
                    },
                    session=session)
                # return True
            # except pymongo_errors.PyMongoError as e:
            #     print(e)
            #     print('error!!!!!!')
            #     return False


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
