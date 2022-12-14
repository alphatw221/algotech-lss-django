
from datetime import datetime
from http import client
import json
import traceback
from django.core.files.base import ContentFile
from django.contrib.auth.models import User as AuthUser
from django.http import HttpResponseRedirect

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser,FileUploadParser, BaseParser
from rest_framework.renderers import HTMLFormRenderer,StaticHTMLRenderer

import  base64

from api import models
import factory
import service
import lib
import pendulum
import database
from automation import jobs

class MyParser(FormParser):
    media_type = 'text/html'


class DeliveryViewSet(viewsets.GenericViewSet):
    queryset = AuthUser.objects.none()

    @action(detail=False, methods=['PUT'], url_path=r'ecpay/create/delivery_order/(?P<order_oid>[^/.]+)', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_create_delivery_order(self, request, order_oid):
        
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        sub_data = request.data
        params = {
            'delivery_service': 'ecpay',
            "order_oid": order_oid,
            "order": order,
            "extra_data": sub_data
        }
        reponse = lib.helper.delivery_helper.DeliveryHelper.create_delivery_order(**params)
        if not reponse.get("RtnMsg", None):
            raise lib.error_handle.error.api_error.ApiVerifyError('create_delivery_order_fail')
        return Response(reponse, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'/ecpay/create/delivery_order/callback/(?P<order_oid>[^/.]+)', parser_classes=(FormParser,MultiPartParser), renderer_classes = (StaticHTMLRenderer,),permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_delivery_order_callback(self, request, order_oid):
        try:
            data = request.data.dict()
            order = lib.util.verify.Verify.get_order_with_oid(order_oid)
            campaign = lib.util.verify.Verify.get_campaign_from_order(order)
            meta = order.meta
            meta["ecpay_delivery_callback"] = data
            serializer = models.order.order.OrderSerializerUpdatePaymentShipping(order, data=meta, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            order = serializer.save()
            
            params = {
                "order_oid": order_oid,
                "order": order,
                "extra_data": {},
                "create_order": False
            }
            reponse = lib.helper.delivery_helper.DeliveryHelper.update_delivery_status(**params)
            #TODO #save this callback data
            # {'CVSValidationNo': '',
            #  'ReceiverEmail': 'test@gmail.com',
            #  'UpdateStatusDate': '2022/12/09 15:20:18',
            #  'BookingNote': '901355249391',
            #  'LogisticsSubType': 'TCAT',
            #  'MerchantTradeNo': '3363320221209062838',
            #  'LogisticsType': 'HOME',
            #  'ReceiverCellPhone': '0933222111', 
            #  'CVSPaymentNo': '',
            #  'RtnMsg': '訂單上傳處理中',
            #  'GoodsAmount': '350',
            #  'AllPayLogisticsID': '27379122',
            #  'MerchantID': '3344643',
            #  'ReceiverName': '測試收件者',
            #  'CheckMacValue': '3A9D2933255F4E28B638FD99787BF94C',
            #  'RtnCode': '310',
            #  'ReceiverPhone': '0226550115',
            #  'ReceiverAddress': '台北市南港區三重路19-2號5樓D棟'
            #  }
        except:
            print(traceback.format_exc())
        
        return Response('ok', status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['GET'], url_path=r'stripe/gateway', permission_classes=(),  authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_stripe_gateway(self, request):
        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)

        if not campaign.meta_payment.get("stripe",{}).get("enabled"):
            raise lib.error_handle.error.api_error.ApiVerifyError('payment_not_enable')
            
        secret = campaign.meta_payment.get("stripe",{}).get("secret")
        currency = campaign.meta_payment.get("stripe",{}).get("currency")

        checkout_session = service.stripe.stripe.create_checkout_session(
            secret,
            currency,
            order,
            campaign.decimal_places,
            campaign.price_unit,
            success_url=settings.GCP_API_LOADBALANCER_URL + '/api/v2/payment/stripe/callback/success?session_id={CHECKOUT_SESSION_ID}&order_oid=' + str(order_oid), 
            cancel_url=f'{settings.WEB_SERVER_URL}/buyer/order/{str(order_oid)}/payment')

        if not checkout_session:
            raise lib.error_handle.error.api_error.ApiCallerError('choose_another_payment_method')
        
        return Response(checkout_session.url, status=status.HTTP_200_OK)

    