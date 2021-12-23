from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign_product import CampaignProduct
from api.models.order.pre_order import PreOrder, PreOrderSerializer
from api.models.order.order import Order, OrderSerializer, OrderSerializerUpdateShipping,api_order_template

from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError, platform_dict
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import F

from api.models.order.order_product import OrderProduct, OrderProductSerializer,api_order_product_template
from django.conf import settings

import functools
from backend.pymongo.mongodb import db, client


def getparams(request, params: tuple, seller=True):
    if seller:
        if not request.user.api_users.filter(type='user').exists():
            raise ApiVerifyError('no api_user found')
        ret = [request.user.api_users.get(type='user')]
    else:
        if not request.user.api_users.filter(type='customer').exists():
            raise ApiVerifyError('no api_user found')
        ret = [request.user.api_users.get(type='customer')]
    for param in params:
        ret.append(request.query_params.get(param))
    return ret


def api_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     print(e)
        #     return Response({"message": str(datetime.now())+"server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper


def verify_buyer_request(api_user, platform_name, campaign_id, order_product_id=None, campaign_product_id=None):
    
    if platform_name not in platform_dict:
        raise ApiVerifyError("no platfrom name found")
    
    if platform_name=='facebook':
        customer_id=api_user.facebook_info['id']
    else:
        raise ApiVerifyError('platform not support')

    if not PreOrder.objects.filter(platform=platform_name, customer_id=customer_id, campaign_id=campaign_id).exists():
        raise ApiVerifyError('no pre_order found')
    pre_order =PreOrder.objects.get(platform=platform_name, customer_id=customer_id, campaign_id=campaign_id)
    
    if order_product_id:
        if not pre_order.order_products.filter(id=order_product_id).exists():
            raise ApiVerifyError("no order_product found")
        order_product = pre_order.order_products.get(
            id=order_product_id)
        campaign_product = order_product.campaign_product

        return pre_order, campaign_product, order_product

    if campaign_product_id:
        if not pre_order.campaign.products.filter(id=campaign_product_id).exists():
            raise ApiVerifyError("no campaign_product found")
        campaign_product = pre_order.campaign.products.get(
            id=campaign_product_id)
        if campaign_product.type=='lucky_draw' or campaign_product.type=='lucky_draw-fast':
            raise ApiVerifyError("invalid campaign_product")
        return pre_order, campaign_product

    return pre_order

def verify_seller_request(api_user, platform_name, platform_id, campaign_id, pre_order_id=None, order_product_id=None, campaign_product_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    if pre_order_id:
        if not campaign.pre_orders.filter(id=pre_order_id).exists():
            raise ApiVerifyError('no pre_order found')
        pre_order = campaign.pre_orders.get(id=pre_order_id)

        if order_product_id:
            if not pre_order.order_products.filter(id=order_product_id).exists():
                raise ApiVerifyError("no order_product found")
            order_product = pre_order.order_products.get(
                id=order_product_id)
            campaign_product = order_product.campaign_product
            return platform, campaign, pre_order, campaign_product, order_product

        if campaign_product_id:
            if not pre_order.campaign.products.filter(id=campaign_product_id).exists():
                raise ApiVerifyError("no campaign_product found")
            campaign_product = pre_order.campaign.products.get(
                id=campaign_product_id)
            return platform, campaign, pre_order, campaign_product

        return platform, campaign, pre_order

    return platform, campaign


class PreOrderPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = PreOrder.objects.all().order_by('id')
    serializer_class = PreOrderSerializer
    filterset_fields = []

    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve')
    @api_error_handler
    def seller_retrieve_pre_order(self, request, pk=None):
        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, _, pre_order = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller_list')
    @api_error_handler
    def seller_list_pre_order(self, request):
        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, campaign = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id)

        queryset = campaign.pre_orders.all()
        # TODO filtering
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PreOrderSerializer(page, many=True)
            result = self.get_paginated_response(
                serializer.data)
            data = result.data
        else:
            serializer = PreOrderSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_checkout')
    @api_error_handler
    def seller_pre_order_checkout(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, _, pre_order = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_add')
    @api_error_handler
    def seller_add_order_product(self, request, pk=None):
        api_user, platform_id, platform_name, campaign_id, campaign_product_id, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "campaign_product_id", "qty"))

        _, _, pre_order, campaign_product = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk, campaign_product_id=campaign_product_id)

        api_order_product = PreOrderHelper.add_product(
            api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_update')
    @api_error_handler
    def seller_update_order_product(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id, order_product_id, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "order_product_id", "qty"))

        _, _, pre_order, campaign_product, order_product = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk, order_product_id=order_product_id)

        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_delete')
    @api_error_handler
    def seller_delete_order_product(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id, order_product_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "order_product_id"))

        _, _, pre_order, campaign_product, order_product = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk, order_product_id=order_product_id)

        PreOrderHelper.delete_product(
            api_user, pre_order, order_product, campaign_product)
        return Response({'message':"delete success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_retrieve')
    @api_error_handler
    def buyer_retrieve_pre_order(self, request):
        api_user, platform_name, campaign_id = getparams(
            request, ("platform_name", "campaign_id"), seller=False)

        pre_order = verify_buyer_request(
            api_user, platform_name, campaign_id)

        serializer = PreOrderSerializer(pre_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_checkout')
    @api_error_handler
    def buyer_pre_order_checkout(self, request):

        api_user, platform_name, campaign_id = getparams(
            request, ("platform_name", "campaign_id"), seller=False)
            
        pre_order = verify_buyer_request(
            api_user, platform_name, campaign_id)
        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_add')
    @api_error_handler
    def buyer_add_order_product(self, request):
        api_user, platform_name, campaign_id, campaign_product_id, qty = getparams(
            request, ("platform_name", "campaign_id", "campaign_product_id", "qty"), seller=False)

        pre_order, campaign_product = verify_buyer_request(
            api_user, platform_name, campaign_id, campaign_product_id=campaign_product_id)

        api_order_product = PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_update')
    @api_error_handler
    def buyer_update_order_product(self, request):
        api_user, platform_name, campaign_id, order_product_id, qty = getparams(
            request, ("platform_name", "campaign_id", "order_product_id", "qty"), seller=False)

        pre_order, campaign_product, order_product = verify_buyer_request(
            api_user, platform_name, campaign_id, order_product_id=order_product_id)

        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_delete')
    @api_error_handler
    def buyer_delete_order_product(self, request):
        api_user, platform_name, campaign_id, order_product_id= getparams(
            request, ("platform_name", "campaign_id", "order_product_id"), seller=False)

        pre_order, campaign_product, order_product = verify_buyer_request(
            api_user, platform_name, campaign_id, order_product_id=order_product_id)

        PreOrderHelper.delete_product(
            api_user, pre_order, order_product, campaign_product)
        return Response({'message':"delete success"}, status=status.HTTP_200_OK)
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
        