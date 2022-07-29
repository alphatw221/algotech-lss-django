
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
        order.history[models.order.order.PAYMENT_METHOD_STRIPE]={
            "action": "pay",
            "time": pendulum.now("UTC").to_iso8601_string()
        }
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
            currency,order.id,
            f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/hit_pay_return_redirect/?order_id={order.id}',
            f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/hit_pay_webhook/')

        if code != 201:
            raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')

        return Response(payment.get('url'))

    # @action(detail=False, methods=['POST'], url_path=r'hit_pay_webhook', parser_classes=(MultiPartParser, FormParser))
    # def hit_pay_webhook(self, request):
    #     data_dict = request.data.dict()
    #     payment_id, payment_request_id, phone = data_dict['payment_id'], data_dict['payment_request_id'], data_dict['phone']
    #     amount, currency, status = data_dict['amount'], data_dict['currency'], data_dict['status']
    #     order_id = data_dict['reference_number']
    #     _hmac, secret_salt = data_dict['hmac'], settings.HITPAY_SECRET_SALT
    #     sort_key_list = ['amount', 'currency', 'hmac', 'payment_id', 'payment_request_id', 'phone', 'reference_number', 'status']

    #     hitpay_dict, info_dict = {}, {}
    #     info_dict['payment_id'] = payment_id
    #     info_dict['payment_request_id'] = payment_request_id
    #     hitpay_dict['hitpay'] = info_dict
    #     total = int(db.api_order.find_one({'id': int(order_id)})['total'])

    #     #TODO change to real checking way
    #     if status == 'completed' and int(total) == int(float(amount)):
    #         db.api_order.update_one(
    #             { 'id': int(order_id) },
    #             { '$set': {'status': 'complete', 'checkout_details': hitpay_dict, 'payment_method': 'hitpay'} }
    #         )

    #     send_email(order_id)
    #     # shop, order, campaign = confirmation_email_info(order_id)
    #     # sib_service.transaction_email.OrderConfirmationEmail(shop=shop, order=order, campaign=campaign, to=[order.get('shipping_email')], cc=[]).send()

    #     return Response('hitpay succed')
    
    # @action(detail=False, methods=['GET'], url_path=r'hit_pay_return_redirect')
    # @api_error_handler
    # def hit_pay_redirect(self, request):
    #     order_id, status = request.query_params.get('order_id'), request.query_params.get('status') 
    #     if status == 'canceled':
    #         return redirect(settings.WEB_SERVER_URL + '/buyer/order/' + order_id + '/payment')
    #     time.sleep(2)
    #     order_object = Verify.get_order(order_id)
    #     campaign = order_object.campaign
    #     api_key = campaign.meta_payment.get("hitpay").get("hitpay_api_key")

    #     payment_request_id = db.api_order.find_one({'id': int(order_id)})['checkout_details']['hitpay']['payment_request_id']

    #     headers = {
    #         'X-BUSINESS-API-KEY': api_key,
    #         'Content-Type': 'application/x-www-form-urlencoded',
    #         'X-Requested-With': 'XMLHttpRequest'
    #     }
    #     params = {
    #         'ID': payment_request_id
    #     }
    #     code, ret = HitPay_Helper.HitPayApiCaller(headers=headers, params=params).get()
    #     #TODO return redirect to order history page
    #     if code != 200:
    #         raise Exception('hitpay get payment request api failed')
        
    #     for _ret in ret:
    #         if _ret['id'] == payment_request_id:
    #             status = _ret['status']
    #     if status == 'completed':
    #         return redirect(settings.WEB_SERVER_URL + '/buyer/order/' + order_id + '/confirmation')