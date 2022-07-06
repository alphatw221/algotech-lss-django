
from django.core.files.base import ContentFile
from django.contrib.auth.models import User as AuthUser
from django.http import HttpResponseRedirect

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.parsers import MultiPartParser


import  base64

from api import models
import service
import lib
import pendulum
import database
from automation import jobs

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

        if not campaign.meta_payment.get("stripe",{}).get("enabled"):
            raise lib.error_handle.error.api_error.ApiVerifyError('payment not enable')
            
        secret = campaign.meta_payment.get("stripe",{}).get("secret")
        currency = campaign.meta_payment.get("stripe",{}).get("currency")

        checkout_session = service.stripe.stripe.create_checkout_session(
            secret,
            currency,
            order,
            success_url=settings.GCP_API_LOADBALANCER_URL + '/api/v2/payment/strip/callback/success?session_id={CHECKOUT_SESSION_ID}&order_oid=' + str(order_oid), 
            cancel_url=f"{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/strip/callback/cancel?order_oid={str(order_oid)}")

        if not checkout_session:
            raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')
        
        return Response(checkout_session.url, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'strip/callback/success',)
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def strip_success_callback(self, request):
        print("session_id", request.GET["session_id"])

        session_id, order_oid = lib.util.getter.getparams(request, ('session_id', 'order_oid'), with_user=False)

        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = order.campaign

        secret = campaign.meta_payment.get("stripe",{}).get("secret")
        is_successful, payment_intent = service.stripe.stripe.is_payment_successful(secret, session_id)
        
        if not is_successful:
            raise lib.error_handle.error.api_error.ApiVerifyError('payment not successful')

        after_pay_details = {
            "client_secret": payment_intent.client_secret,
            "id": payment_intent.id,
            "object": payment_intent.object,
            "receipt_email": payment_intent.receipt_email,
            "receipt_url": payment_intent.charges.data[0].receipt_url,
        }
        order.status = models.order.order.STATUS_COMPLETE
        order.payment_method = models.order.order.PAYMENT_METHOD_STRIPE
        order.checkout_details[models.order.order.PAYMENT_METHOD_STRIPE] = after_pay_details
        order.history.append({
            "action": "pay",
            "time": pendulum.now("UTC").to_iso8601_string()
        })
        order.save()

        content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
        jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)
        return HttpResponseRedirect(redirect_to=f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}/confirmation')

    @action(detail=False, methods=['GET'], url_path=r'strip/callback/cancel', )
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def strip_cancel_callback(self, request):
        order_oid, = lib.util.getter.getparams(request, ('order_oid',), with_user=False)
        return HttpResponseRedirect(
                redirect_to=f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}/payment')

        # session_id, order_id = lib.util.getter.getparams(request, ('session_id', 'order_id'), with_user=False)

        # order = lib.util.verify.Verify.get_order(order_id)
        # campaign = order.campaign

        # secret = campaign.meta_payment.get("stripe",{}).get("secret")
        # is_successful, payment_intent = service.stripe.stripe.is_payment_successful(secret, session_id)


        # try:
        #     order_id = request.GET["order_id"]
        #     order_object = Verify.get_order(order_id)
        #     order_object.history[str(len(order_object.history) + 1)] = {
        #         "action": "back",
        #         "time": pendulum.now("UTC").to_iso8601_string()
        #     }
        #     order_object.save()
        #     return HttpResponseRedirect(
        #         redirect_to=f'{settings.WEB_SERVER_URL}/buyer/order/{order_object.id}/payment')
        # except Exception as e:
        #     print(e)
        #     return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    # @action(detail=False, methods=['GET'], url_path=r'first_data/credential', permission_classes=(),  authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def get_first_data_credential(self, request):
    #     order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
    #     order = lib.util.verify.Verify.get_order_with_oid(order_oid)
    #     campaign = lib.util.verify.Verify.get_campaign_from_order(order)

    #     firstdata = campaign.meta_payment.get('first_data',{})   #TODO REMOVE SG layer

    #     if not firstdata.get("enable"):
    #         raise lib.error_handle.error.api_error.ApiVerifyError('payment not enable')

    #     chargetotal = order.total
    #     currency = firstdata.get('currency')
    #     storeId = firstdata.get('storeId')
    #     timezone = firstdata.get('timezone')
    #     sharedSecret = firstdata.get('sharedSecret')
    #     txndatetime = lib.helper.first_data_helper.getDateTime(timezone)

    #     credential = {
    #         "storename" : storeId,
    #         "txntype" : "sale",
    #         "mode" : "payonly",
    #         "timezone" : timezone,
    #         "txndatetime" : txndatetime,
    #         "responseSuccessURL" : f"{settings.GCP_API_LOADBALANCER_URL}/api/payment/ipg_payment_success/?order_id={order.id}",
    #         "responseFailURL" : f"{settings.GCP_API_LOADBALANCER_URL}/api/payment/ipg_payment_fail/?order_id={order.id}",
    #         "hash_algorithm" : "SHA256",
    #         "hash":lib.helper.first_data_helper.createHash(chargetotal,currency,storeId,sharedSecret,timezone,txndatetime),
    #         "chargetotal" : chargetotal,
    #         "currency" : currency,
    #     }
        
    #     return Response({"url":"https://www4.ipg-online.com/connect/gateway/processing","credential":credential}, status=status.HTTP_200_OK)
    #     return Response(checkout_session.url, status=status.HTTP_303_SEE_OTHER)
