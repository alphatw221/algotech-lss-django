
from http import client
import json
from django.core.files.base import ContentFile
from django.contrib.auth.models import User as AuthUser
from django.http import HttpResponseRedirect

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser,FileUploadParser, BaseParser
from rest_framework.renderers import HTMLFormRenderer

import  base64

from api import models
from api.utils.error_handle.error.api_error import ApiCallerError
import service
import lib
import pendulum
import database
from automation import jobs

class MyParser(FormParser):
    media_type = 'text/html'


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
            cancel_url=f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{str(order_oid)}/payment')

        if not checkout_session:
            raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')
        
        return Response(checkout_session.url, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'stripe/callback/success',)
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
        order.history[models.order.order.PAYMENT_METHOD_STRIPE]={
            "action": "pay",
            "time": pendulum.now("UTC").to_iso8601_string()
        }
        order.save()

        content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
        jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)
        return HttpResponseRedirect(redirect_to=f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}/confirmation')

    # @action(detail=False, methods=['GET'], url_path=r'strip/callback/cancel', )
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def strip_cancel_callback(self, request):
    #     order_oid, = lib.util.getter.getparams(request, ('order_oid',), with_user=False)
    #     return HttpResponseRedirect(
    #             redirect_to=f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}/payment')

    

    @action(detail=False, methods=['GET'], url_path=r'hitpay/gateway')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_hitpay_gateway(self, request):
        
        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)

        api_key = campaign.meta_payment.get("hitpay",{}).get("api_key")
        currency = campaign.meta_payment.get("hitpay",{}).get("currency")

        code, payment = service.hitpay.hitpay.create_payment(
            api_key,
            order.shipping_email, 
            order.total, 
            currency,
            order.id,
            f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}',
            f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/hitpay/webhook/')

        if code != 201:
            raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')

        return Response(payment.get('url'))

    @action(detail=False, methods=['POST'], url_path=r'hitpay/webhook', parser_classes=(MultiPartParser, FormParser))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def hit_pay_webhook(self, request):

        amount, status, reference_number, hmac,  = \
            lib.util.getter.getdata(request, ("amount", "status", "reference_number", "hmac"), required=True)

        order = lib.util.verify.Verify.get_order(reference_number)
        campaign = order.campaign
        salt = campaign.meta_payment.get(models.order.order.PAYMENT_METHOD_HITPAY,{}).get('salt')
        
        if not lib.helper.hitpay_helper.is_request_valid(request, salt, hmac):
            raise lib.error_handle.error.api_error.ApiCallerError('invalid')

        if status == 'completed' :

            order.status = models.order.order.STATUS_COMPLETE
            order.payment_method = models.order.order.PAYMENT_METHOD_HITPAY
            order.checkout_details[models.order.order.PAYMENT_METHOD_HITPAY] = request.data.dict()
            order.history[models.order.order.PAYMENT_METHOD_HITPAY]={
                "action": "pay",
                "time": pendulum.now("UTC").to_iso8601_string()
            }
            order.save()

            content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
            jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)
        return Response('ok')






    @action(detail=False, methods=['GET'], url_path=r"paypal/gateway")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_paypal_gateway(self, request):

        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)

        client_id = campaign.meta_payment.get("paypal",{}).get("client_id")
        secret = campaign.meta_payment.get("paypal",{}).get("secret")
        currency = campaign.meta_payment.get("paypal",{}).get("currency")

        payment = service.paypal.paypal.create_payment(client_id, secret, order.total, currency , 
            f"{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/paypal/callback/success?order_oid={order_oid}", 
            f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}',
            )
        if not payment:
            raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')


        for link in payment.links:
            if link.rel == "approval_url":
                return Response(str(link.href))
        
        raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')

    @action(detail=False, methods=['GET'], url_path=r"paypal/callback/success")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def paypal_success_callback(self, request):

        paymentId, PayerID, order_oid = lib.util.getter.getparams(request, ('paymentId', 'PayerID', 'order_oid'), with_user=False)
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = order.campaign
        client_id = campaign.meta_payment.get("paypal",{}).get("client_id")
        secret = campaign.meta_payment.get("paypal",{}).get("secret")

        payment = service.paypal.paypal.find_payment(client_id, secret, paymentId)

        if not payment or not payment.execute({"payer_id": PayerID}):
            return Response(payment.error)

        order.status = models.order.order.STATUS_COMPLETE
        order.payment_method = models.order.order.PAYMENT_METHOD_PAYPAL
        order.checkout_details[models.order.order.PAYMENT_METHOD_PAYPAL] = request.data
        order.history[models.order.order.PAYMENT_METHOD_PAYPAL]={
            "action": "pay",
            "time": pendulum.now("UTC").to_iso8601_string()
        }
        order.save()

        content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
        jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)
        return HttpResponseRedirect(redirect_to=f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}/confirmation')


    @action(detail=False, methods=['GET'], url_path=r"pay_mongo/gateway")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_pay_mongo_gateway(self, request):
        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)
        secret_key = campaign.meta_payment.get("pay_mongo",{}).get("secret")
        
        response = service.pay_mongo.pay_mongo.retrieve_webhook(secret_key)
        if response.status_code != 200:
            raise ApiCallerError(f"error: {response.json()}")
        
        webhook_exists = False
        webhook_url = 'https://staginglss.accoladeglobal.net/api/v2/payment/pay_mongo/webhook/'
        webhook_list = [ value for list_data in response.json()['data'] for key, value in list_data['attributes'].items() if key == 'url']
        if webhook_url in webhook_list:
            webhook_exists = True
        print(webhook_list)
        if not webhook_exists:
            response = service.pay_mongo.pay_mongo.register_webhook(secret_key, webhook_url)
            if response.status_code != 200:
                raise ApiCallerError(f"error: {response.json()}")
        
        response = service.pay_mongo.pay_mongo.create_link(order, secret_key)
        if response.status_code != 200:
            raise ApiCallerError(f"error: {response.json()}")
        payMongoResponse = json.loads(response.text)
        print(payMongoResponse)
        return Response(payMongoResponse['data']['attributes']['checkout_url'], status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r"pay_mongo/webhook/register")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def pay_mongo_register_webhook(self, request):
        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)
        secret_key = campaign.meta_payment.get("pay_mongo",{}).get("secret")
        response = service.pay_mongo.pay_mongo.register_webhook(secret_key)
        if response.status_code != 200:
            raise ApiCallerError("error: {response.text}")
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r"pay_mongo/webhook")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def pay_mongo_webhook_paid(self, request):
        from backend.pymongo.mongodb import db
        print(request.data)
        order_id = int(request.data['data']['attributes']['data']['attributes']['description'].split('_')[1])
        if (request.data['data']['attributes']['data']['attributes']['status'] == 'paid'):
            db.api_order.update(
                {'id': order_id},
                {'$set': {'status': 'complete'}}
            )
        return Response('response', status=status.HTTP_200_OK)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    # @action(detail=False, methods=['GET'], url_path=r"paypal_cancel")
    # @api_error_handler
    # def paypal_cancel(self, request, *args, **kwargs):
    #     try:
    #         order_id = request.GET["order_id"]
    #         order_object = Verify.get_order(order_id)
    #         pre_order = PreOrder.objects.filter(customer_id=order_object.customer_id, campaign_id=order_object.campaign_id)
    #         if len(pre_order) > 1:
    #             return Response({"message": "Buyer has more than one shopping cart."}, status=status.HTTP_400_BAD_REQUEST)
    #         order_object.checkout_details[len(order_object.checkout_details) + 1] = {
    #             "action": "cancel payment",
    #             "time": datetime.datetime.now()
    #         }
    #         order_object.save()
    #         return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/cart/{pre_order.id}')
    #     except Exception as e:
    #         print(e)
    #         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['GET'], url_path=r"ecpay/credential")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_ecpay_credential(self, request):

        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)

        merchant_id = campaign.meta_payment.get("ecpay",{}).get("merchant_id")
        hash_key = campaign.meta_payment.get("ecpay",{}).get("hash_key")
        hash_iv = campaign.meta_payment.get("ecpay",{}).get("hash_iv")
        
        action,payment = service.ecpay.ecpay.create_order(merchant_id, hash_key, hash_iv, int(order.total) , order.id, 
            f'https://staginglss.accoladeglobal.net/api/v2/payment/ecpay/callback/success/?order_oid={order_oid}', 
            f'https://staginglss.accoladeglobal.net/buyer/order/{order_oid}',
            )
        
        if not payment:
            raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')


        # for link in payment.links:
        #     if link.rel == "approval_url":
                # return Response(str(link.href))
        return Response({'action':action,'data':payment})
        
        raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')
    
    @action(detail=False, methods=['POST'], url_path=r"ecpay/callback/success",parser_classes=(MultiPartParser,), renderer_classes = (HTMLFormRenderer,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def ecpay_success_callback(self, request):

        # order_oid = lib.util.getter.getparams(request, ('order_oid'), with_user=False)
        # order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        # campaign = order.campaign
        # merchant_id = campaign.meta_payment.get("ecpay",{}).get("merchant_id")
        # hash_key = campaign.meta_payment.get("ecpay",{}).get("hash_key")
        # hash_iv = campaign.meta_payment.get("ecpay",{}).get("hash_iv")
        print("~~~~45df45df4g5s4524sgh254s25gf4~~~~~~")
        print(request)

        # payment = service.paypal.paypal.find_payment(client_id, secret, paymentId)

        # if not payment or not payment.execute({"payer_id": PayerID}):
        #     return Response(payment.error)

        # order.status = models.order.order.STATUS_COMPLETE
        # order.payment_method = models.order.order.PAYMENT_METHOD_PAYPAL
        # order.checkout_details[models.order.order.PAYMENT_METHOD_PAYPAL] = request.data
        # order.history[models.order.order.PAYMENT_METHOD_PAYPAL]={
        #     "action": "pay",
        #     "time": pendulum.now("UTC").to_iso8601_string()
        # }
        # order.save()

        # content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
        # jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)
        # return HttpResponseRedirect(redirect_to=f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}/confirmation')

        return Response('1|OK')
        