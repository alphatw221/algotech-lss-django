
from django.core.files.base import ContentFile
from django.contrib.auth.models import User as AuthUser

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.parsers import MultiPartParser


import  base64

import service
import lib


class PaymentViewSet(viewsets.GenericViewSet):
    queryset = AuthUser.objects.none()

    # @action(detail=False, methods=['PUT'], url_path=r'receipt/upload', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def upload_transfer_receipt(self, request):
    #     order_id, last_five_digit, image = lib.util.getter.getdata(request,('order_id', 'last_five_digit', 'image'), required = True) 
        
    #     return Response({"message": "upload succeed"}, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['GET'], url_path=r'stripe/gateway', permission_classes=(),  authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_stripe_gateway(self, request):
        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)

        if not campaign.meta_payment.get("stripe",{}).get("enable"):
            raise lib.error_handle.error.api_error.ApiVerifyError('payment not enable')
            
        secret = campaign.meta_payment.get("stripe",{}).get("secret")
        currency = campaign.meta_payment.get("stripe",{}).get("currency")

        checkout_session = service.stripe.stripe.create_checkout_session(
            secret,
            currency,
            order,
            success_url=settings.GCP_API_LOADBALANCER_URL + '/api/payment/strip_success?session_id={CHECKOUT_SESSION_ID}&order_id=' + str(order.id), 
            cancel_url=f"{settings.GCP_API_LOADBALANCER_URL}/api/payment/strip_cancel?order_id={order.id}")

        if not checkout_session:
            raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')
        
        return Response(checkout_session.url, status=status.HTTP_303_SEE_OTHER)


    @action(detail=False, methods=['GET'], url_path=r'first_data/credential', permission_classes=(),  authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_first_data_credential(self, request):
        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)

        firstdata = campaign.meta_payment.get('first_data',{})   #TODO REMOVE SG layer

        if not firstdata.get("enable"):
            raise lib.error_handle.error.api_error.ApiVerifyError('payment not enable')

        chargetotal = order.total
        currency = firstdata.get('currency')
        storeId = firstdata.get('storeId')
        timezone = firstdata.get('timezone')
        sharedSecret = firstdata.get('sharedSecret')
        txndatetime = lib.helper.first_data_helper.getDateTime(timezone)

        credential = {
            "storename" : storeId,
            "txntype" : "sale",
            "mode" : "payonly",
            "timezone" : timezone,
            "txndatetime" : txndatetime,
            "responseSuccessURL" : f"{settings.GCP_API_LOADBALANCER_URL}/api/payment/ipg_payment_success/?order_id={order.id}",
            "responseFailURL" : f"{settings.GCP_API_LOADBALANCER_URL}/api/payment/ipg_payment_fail/?order_id={order.id}",
            "hash_algorithm" : "SHA256",
            "hash":lib.helper.first_data_helper.createHash(chargetotal,currency,storeId,sharedSecret,timezone,txndatetime),
            "chargetotal" : chargetotal,
            "currency" : currency,
        }
        
        return Response({"url":"https://www4.ipg-online.com/connect/gateway/processing","credential":credential}, status=status.HTTP_200_OK)


    
        return Response(checkout_session.url, status=status.HTTP_303_SEE_OTHER)
