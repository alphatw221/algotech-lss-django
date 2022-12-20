from math import floor

from business_policy.delivery import DeliveryMeta
import service
from django.conf import settings
from api import models

class DeliveryHelper():
    DELIVERY_STATUS_AWAITING_FULFILLMENT = 'awaiting_fulfillment'
    DELIVERY_STATUS_AWAITING_SHIPMENT = 'awaiting_shipment'
    DELIVERY_STATUS_AWAITING_PICKUP = 'awaiting_pickup'
    DELIVERY_STATUS_PARTIALLY_SHIPPED = 'partially_shipped'
    DELIVERY_STATUS_SHIPPED = 'shipped'
    DELIVERY_STATUS_COLLECTED = 'collected'
    DELIVERY_STATUS_AWAITING_RETURN = 'awaiting_return'
    DELIVERY_STATUS_RETURNED = 'returned'
    
    @classmethod
    def get_delivery_service(cls, **kwargs):
        delivery_service = ""
        order = kwargs.get('order')
        countrys = order.user_subscription.meta_country.get("activated_country", [])
        
        support_delivery_services = set()
        for country in countrys:
            support_delivery_service = DeliveryMeta().get_support_delivery(country)
            for service in support_delivery_service:
                support_delivery_services.add(service)
        
        for service in support_delivery_services:
            if order.shipping_method == service:
                delivery_service = service
                break
        return delivery_service
    
    @classmethod
    def create_delivery_order(cls, delivery_service, order_oid, order, extra_data):
        print("create_delivery_order")
        delivery_order = {}
        if delivery_service == "ecpay":
            delivery_order = cls.__create_ecpay_delivery_order(order_oid, order, extra_data)
        return delivery_order
    
    @classmethod
    def create_delivery_order_and_update_delivery_status(cls, **kwargs): ## order, create_order
        print("create_delivery_order_and_update_delivery_status")
        delivery_order = {}
        
        order_oid = kwargs.get('order_oid')
        order = kwargs.get('order')
        delivery_service = order.shipping_method
        extra_data = kwargs.get('extra_data')
        need_create_delivery_order = kwargs.get('create_order') ## True or False
        need_update_delivery_status = kwargs.get('update_status') ## True or False
        
        if need_create_delivery_order:
            delivery_order = cls.create_delivery_order(delivery_service, order_oid, order, extra_data)
        if need_update_delivery_status:
            cls.update_delivery_status(delivery_service, delivery_order, order)
        return delivery_order
        
    @classmethod
    def update_delivery_status(cls, delivery_service, delivery_order, order): ## order, create_order
        print("update_delivery_status")
        delivery_status = order.delivery_status
        if delivery_service == "ecpay":
            delivery_status = cls.__ecpay_delivery_status_map(delivery_order)
        if delivery_status:
            order.delivery_status = delivery_status
            order.save()
    
    @classmethod
    def __create_ecpay_delivery_order(cls, order_oid, order, extra_data={}):
        #TODO #根據seller setting 決定是否使用綠界物流，線上付款後再成立delivery order
        print("create_ecpay_delivery_order")
        response = service.ecpay.ecpay.create_shipping_order(
            order, 
            f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/delivery/ecpay/create/delivery_order/callback/{order_oid}/',
            extra_data
        )
        
        print("response", response)
        return response
    @classmethod
    def __ecpay_delivery_status_map(cls, delivery_order):
        if not delivery_order:
            return None
        
        LogisticsType = delivery_order.get("LogisticsType", False)
        if not LogisticsType:
            return None
        
        ecapy_delivery_status = delivery_order.get("RtnCode", False)
        if not ecapy_delivery_status:
            return None
        
        delivery_status_map = {
            "CVS":{
                "300": models.order.order.DELIVERY_STATUS_AWAITING_SHIPMENT, # 訂單處理中(已收到訂單資料)
                "3022": models.order.order.DELIVERY_STATUS_COLLECTED, # 買家已到店取貨
                "3032": models.order.order.DELIVERY_STATUS_SHIPPED, # 賣家已到門市寄件
            },
            "HOME": {
                "300": models.order.order.DELIVERY_STATUS_AWAITING_SHIPMENT, # 訂單處理中(已收到訂單資料)
                "3003": models.order.order.DELIVERY_STATUS_COLLECTED, # 配完
                "3006": models.order.order.DELIVERY_STATUS_SHIPPED, # 配送中
            }
            
        }
        return delivery_status_map.get(LogisticsType, {}).get(ecapy_delivery_status,None)

        
    