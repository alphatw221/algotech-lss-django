from pymongo import message
from backend.pymongo.mongodb import db, client
from django.conf import settings
from datetime import datetime

from api.models.order.order import api_order_template
from api.models.order.order_product import api_order_product_template
from api.utils.common.verify import ApiVerifyError, platform_dict


class PreOrderHelper():

    @classmethod
    def update_product(cls, api_user, pre_order, order_product, campaign_product, qty):
        with client.start_session() as session:
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
                qty_difference = cls._check_stock(
                    api_campaign_product, original_qty=api_order_product['qty'], request_qty=qty)

                db.api_campaign_product.update_one(
                    {'id': api_campaign_product['id']}, {"$inc": {'qty_sold': qty_difference}}, session=session)

                db.api_order_product.update_one(
                    {'id': api_order_product['id']}, {"$set": {'qty': qty}}, session=session)

                products = api_pre_order['products']
                products[str(api_campaign_product['id'])]['qty'] = qty
                db.api_pre_order.update_one(
                    {'id': pre_order.id},
                    {
                        "$set": {
                            "lock_at": datetime.now() if api_user.type == 'customer' else None,
                            "products": products
                        },
                        "$inc": {
                            "total": qty_difference*api_campaign_product['price'],
                        }
                    },
                    session=session)

        return db.api_order_product.find_one({"id": api_order_product['id']},{"_id":False})

    @classmethod
    def add_product(cls, api_user, pre_order, campaign_product, qty):
        with client.start_session() as session:
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

                latest_api_order_product = db.api_order_product.find_one(
                    {"$query": {}, "$orderby": {"id": -1}}, session=session)
                id_increment = latest_api_order_product['id'] + \
                    1 if latest_api_order_product else 1
                template=api_order_product_template.copy()
                template.update({
                    "id": id_increment,
                    "campaign_id": api_campaign_product["campaign_id"],
                    "campaign_product_id": api_campaign_product["id"],
                    "pre_order_id": api_pre_order["id"],
                    "qty": qty,
                    "customer_id": api_pre_order['customer_id'],
                    "customer_name": api_pre_order['customer_name'],
                    "platform": api_pre_order['platform'],
                    "type": api_campaign_product["type"]
                })
                db.api_order_product.insert_one(template, session=session)

                db.api_campaign_product.update_one({"id": campaign_product.id}, {
                                                   "$inc": {'qty_sold': qty_difference}})

                products = api_pre_order['products']
                products[str(api_campaign_product['id'])] = {
                    "price": api_campaign_product['price'], "qty": qty}
                db.api_pre_order.update_one(
                    {'id': pre_order.id},
                    {
                        "$set": {
                            "lock_at": datetime.now() if not api_user or api_user.type == 'customer' else None,
                            "products": products
                        },
                        "$inc": {
                            "total": qty_difference*api_campaign_product['price'],
                        }
                    },
                    session=session)

        return db.api_order_product.find_one({"id": id_increment},{"_id":False})

    @classmethod
    def delete_product(cls, api_user, pre_order, order_product, campaign_product):
        with client.start_session() as session:
            with session.start_transaction():
                api_pre_order = db.api_pre_order.find_one(
                    {"id": pre_order.id}, session=session)
                api_order_product = db.api_order_product.find_one(
                    {"id": order_product.id}, session=session)
                api_campaign_product = db.api_campaign_product.find_one(
                    {"id": campaign_product.id}, session=session)

                cls._check_lock(api_user, api_pre_order)


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
                            "lock_at": datetime.now() if api_user.type == 'customer' else None,
                            "products": products
                        },
                        "$inc": {
                            "total": -api_order_product['qty']*api_campaign_product['price'],
                        }
                    },
                    session=session)
        return True

    @classmethod
    def checkout(cls, api_user, pre_order):
        with client.start_session() as session:
            with session.start_transaction():
                api_pre_order = db.api_pre_order.find_one(
                    {"id": pre_order.id}, session=session)

                cls._check_lock(api_user, api_pre_order)
                cls._check_empty(api_pre_order)

                latest_api_order_product = db.api_order.find_one(
                    {"$query": {}, "$orderby": {"id": -1}}, session=session)
                id_increment = latest_api_order_product['id'] + \
                    1 if latest_api_order_product else 1
                api_order_data = api_pre_order.copy()
                api_order_data['id'] = id_increment
                del api_order_data['_id']
                template=api_order_template.copy()
                template.update(api_order_data)
                db.api_order.insert_one(template, session=session)

                db.api_order_product.update_many(
                    {"pre_order_id": api_pre_order["id"]}, {"$set": {"pre_order_id": None, "order_id": id_increment}})
                db.api_pre_order.update_one({"id": api_pre_order["id"]}, {
                                            "$set": {"products": {}, "total": 0, "subtotal": 0}}, session=session)

        return db.api_order.find_one({"id": id_increment},{"_id":False})
    
    @staticmethod
    def lucky_draw_error_check(pre_order, campaign_product):
        with client.start_session() as session:
            with session.start_transaction():
                api_pre_order = db.api_pre_order.find_one(
                    {"id": pre_order.id}, session=session)
                api_campaign_product = db.api_campaign_product.find_one(
                    {"id": campaign_product.id}, session=session)
                
                message = []
                if str(api_campaign_product["id"]) in api_pre_order["products"]:
                    message.append("product already in pre_order")
                if api_campaign_product['type']=='n/a':
                    message.append("out of stock")
                return message

    @staticmethod
    def _check_platform(platform, customer_id, customer_name):
        pass

    @staticmethod
    def _check_lock(api_user, api_pre_order):
        if not api_user:
            return
        if api_user.type == 'customer':
            return
        if api_pre_order['lock_at'] and datetime.timestamp(api_pre_order['lock_at'])+settings.CART_LOCK_INTERVAL > datetime.timestamp(datetime.now()):
            raise ApiVerifyError('cart in use')

    @staticmethod
    def _check_qty(api_campaign_product, qty):
        if not qty:
            raise ApiVerifyError('please enter qty')
        qty = int(qty)
        if not qty:
            raise ApiVerifyError('qty can not be zero or negitive')
        return qty

    @staticmethod
    def _check_stock(api_campaign_product, original_qty, request_qty):
        qty_difference = int(request_qty)-original_qty
        if qty_difference and api_campaign_product["qty_for_sale"]-api_campaign_product["qty_sold"]< qty_difference:
            raise ApiVerifyError("out of stock")
        return qty_difference

    @staticmethod
    def _check_addable(api_pre_order, api_campaign_product):
        if str(api_campaign_product["id"]) in api_pre_order["products"]:
            raise ApiVerifyError("product already in pre_order")
    @staticmethod
    def _check_empty(api_pre_order):
        if not bool(api_pre_order['products']):
            raise ApiVerifyError('cart is empty')

    @staticmethod
    def _check_type(api_campaign_product):
        if api_campaign_product['type']=='lucky_draw' or api_campaign_product['type']=='lucky_draw-fast':
            api_campaign_product['price']=0
        elif api_campaign_product['type']=='n/a':
            raise ApiVerifyError('out of stock')


class OrderHelper():

    class OrderValidator():
        pass
    
    @classmethod
    def cancel(self, api_user, order):
        with client.start_session() as session:
            with session.start_transaction():
                api_order = db.api_order.find_one(
                    {'id': order.id}, session=session)
                
                campaign_id = api_order['campaign_id']
                customer_id = api_order['customer_id']
                pre_order_id = db.api_pre_order.find_one({'campaign_id': campaign_id, 'customer_id': customer_id})['id']
                
                products_dict = {}
                total_count = 0
                order_products = db.api_order_product.find({'campaign_id': campaign_id, 'customer_id': customer_id, 'order_id': order.id})
                for order_product in order_products:
                    campaign_product_id = order_product['campaign_product_id']
                    price = db.api_campaign_product.find_one({'id': campaign_product_id})['price']
                    product_dict = {}

                    if db.api_order_product.find({'order_id': None, 'campaign_id': campaign_id, 'campaign_product_id': campaign_product_id, "customer_id": customer_id}).count() > 0:
                        pre_order_product = db.api_order_product.find({'order_id': None, 'campaign_id': campaign_id, 'campaign_product_id': campaign_product_id, "customer_id": customer_id})

                        db.api_order_product.update_one(
                            {'pre_order_id': pre_order_id, 'campaign_product_id': campaign_product_id}, 
                            {'$set': 
                                {'qty': order_product['qty'] + pre_order_product['qty']}
                            }
                        )
                        db.api_order_product.delete_one({'order_id': order.id, 'campaign_product_id': campaign_product_id})

                        product_dict['qty'] = order_product['qty'] + pre_order_product['qty']
                        product_dict['price'] = price
                        total_count += (order_product['qty'] + pre_order_product['qty']) * price
                    else:
                        db.api_order_product.update_one(
                            {'order_id': order.id, 'campaign_product_id': campaign_product_id}, 
                            {'$set': 
                                {'pre_order_id': pre_order_id, 'order_id': None}
                            }
                        )

                        product_dict['qty'] = order_product['qty']
                        product_dict['price'] = price
                        total_count += order_product['qty'] * price
                    products_dict[str(campaign_product_id)] = product_dict
                db.api_pre_order.update_one(
                    {'id': pre_order_id},
                    {'$set': 
                        {'products': products_dict, 'total': total_count}
                    }
                )
                db.api_order.delete_one({'id': order.id})

        return pre_order_id
    
    @classmethod
    def delete(self, api_user, order):
        with client.start_session() as session:
            with session.start_transaction():
                api_order = db.api_order.find_one(
                    {'id': order.id}, session=session)

                campaign_id = api_order['campaign_id']
                customer_id = api_order['customer_id']
                order_id = order.id

                order_products = db.api_order_product.find({'campaign_id': campaign_id, 'customer_id': customer_id, 'order_id': order_id})
                for order_product in order_products:
                    campaign_product_id = order_product['campaign_product_id']
                    order_qty = order_product['qty']

                    cp_product = db.api_campaign_product.find_one({'campaign_id': campaign_id, 'id': campaign_product_id})
                    db.api_campaign_product.update_one(
                        {'campaign_id': campaign_id, 'id': campaign_product_id},
                        {'$set': 
                            {'qty_sold': cp_product['qty_sold'] - order_qty}
                        }
                    )
                    db.api_order_product.delete_one({'order_id': order_id, 'campaign_product_id': campaign_product_id})

                db.api_order.delete_one({'id': order_id})