from math import floor

from business_policy.delivery import DeliveryMeta
import service
from django.conf import settings

class DeliveryHelper():
    
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
    def create_delivery_order(cls, **kwargs):
        delivery_order = {}
        delivery_service = kwargs.get("delivery_service")
        if delivery_service == "ecpay":
            delivery_order = cls.__create_ecpay_delivery_order(**kwargs)
        return delivery_order
    
    @classmethod
    def update_delivery_status(cls, **kwargs): ## order, create_order
        delivery_order = {}
        kwargs.update({"delivery_service": cls.get_delivery_service(**kwargs)})
        order = kwargs.get('order')
        need_create_delivery_order = kwargs.get('create_order') ## True or False
        
        if need_create_delivery_order:
            delivery_order = cls.create_delivery_order(**kwargs)
        if delivery_order.get("status", None):
            order.delivery_status = delivery_order.get("status", None)
            order.save()
    
    @classmethod
    def __create_ecpay_delivery_order(cls, order_oid, order, extra_data={}):
        #TODO #根據seller setting 決定是否使用綠界物流，線上付款後再成立delivery order
        print(order_oid)
        print(order)
        print(extra_data)
        response = service.ecpay.ecpay.create_shipping_order(
            order, 
            f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/delivery/ecpay/create/delivery_order/callback/{order_oid}/',
            # f'https://28ea-220-136-105-200.jp.ngrok.io/api/v2/order/{order_oid}/buyer/delivery_order/callback/',
            extra_data
        )
        return response
        
    