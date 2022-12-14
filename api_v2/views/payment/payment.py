
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
            raise lib.error_handle.error.api_error.ApiVerifyError('payment_failed')

        after_pay_details = {
            "client_secret": payment_intent.client_secret,
            "id": payment_intent.id,
            "object": payment_intent.object,
            "receipt_email": payment_intent.receipt_email,
            "receipt_url": payment_intent.charges.data[0].receipt_url,
        }

        order.payment_method = models.order.order.PAYMENT_METHOD_STRIPE
        order.checkout_details[models.order.order.PAYMENT_METHOD_STRIPE] = after_pay_details
        order.history[models.order.order.PAYMENT_METHOD_STRIPE]={
            "action": "pay",
            "time": pendulum.now("UTC").to_iso8601_string()
        }
        #payment status update
        order.paid_at = datetime.utcnow()
        order.payment_status = models.order.order.PAYMENT_STATUS_PAID
        #delivery status update
        lib.helper.delivery_helper.DeliveryHelper.update_delivery_status(**{ "order_oid": order_oid, "order": order, "extra_data": {}, "create_order": True})

        #wallet
        update_wallet(order)

        #send email
        subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
        content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)
        jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)

        #order status update
        lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)
        
        return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/order/{order_oid}/confirmation')

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

        payment_amount = lib.helper.payment_helper.transform_payment_amount(order.total, campaign.decimal_places, campaign.price_unit)

        code, payment = service.hitpay.hitpay.create_payment(
            api_key,
            order.shipping_email, 
            payment_amount, 
            currency,
            order_oid,
            f'{settings.WEB_SERVER_URL}/buyer/order/{order_oid}',
            f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/hitpay/webhook/')

        if code != 201:
            raise lib.error_handle.error.api_error.ApiCallerError('choose_another_payment_method')

        return Response(payment.get('url'))

    @action(detail=False, methods=['POST'], url_path=r'hitpay/webhook', parser_classes=(MultiPartParser, FormParser))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def hit_pay_webhook(self, request):

        amount, status, order_oid, hmac,  = \
            lib.util.getter.getdata(request, ("amount", "status", "reference_number", "hmac"), required=True)
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)
        salt = campaign.meta_payment.get(models.order.order.PAYMENT_METHOD_HITPAY,{}).get('salt')
        
        if not lib.helper.hitpay_helper.is_request_valid(request, salt, hmac):
            raise lib.error_handle.error.api_error.ApiCallerError('invalid')

        if status == 'completed' :
            order.payment_method = models.order.order.PAYMENT_METHOD_HITPAY
            order.checkout_details[models.order.order.PAYMENT_METHOD_HITPAY] = request.data.dict()
            order.history[models.order.order.PAYMENT_METHOD_HITPAY]={
                "action": "pay",
                "time": pendulum.now("UTC").to_iso8601_string()
            }
            order.paid_at = datetime.utcnow()
            #payment status update
            order.payment_status = models.order.order.PAYMENT_STATUS_PAID
            #delivery status update
            lib.helper.delivery_helper.DeliveryHelper.update_delivery_status(**{ "order_oid": order_oid, "order": order, "extra_data": {}, "create_order": True})
            

            #wallet
            update_wallet(order)

            #wallet
            subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
            content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)
            jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
        #order status update
        lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)
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

        payment_amount = lib.helper.payment_helper.transform_payment_amount(order.total, campaign.decimal_places, campaign.price_unit)

        payment = service.paypal.paypal.create_payment(client_id, secret, payment_amount, currency , 
            f"{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/paypal/callback/success?order_oid={order_oid}", 
            f'{settings.WEB_SERVER_URL}/buyer/order/{order_oid}',
            )
        if not payment:
            raise lib.error_handle.error.api_error.ApiCallerError('choose_another_payment_method')


        for link in payment.links:
            if link.rel == "approval_url":
                return Response(str(link.href))
        
        raise lib.error_handle.error.api_error.ApiCallerError('choose_another_payment_method')

    @action(detail=False, methods=['GET'], url_path=r"paypal/callback/success")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def paypal_success_callback(self, request):

        paymentId, PayerID, order_oid = lib.util.getter.getparams(request, ('paymentId', 'PayerID', 'order_oid'), with_user=False)
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)
        client_id = campaign.meta_payment.get("paypal",{}).get("client_id")
        secret = campaign.meta_payment.get("paypal",{}).get("secret")

        payment = service.paypal.paypal.find_payment(client_id, secret, paymentId)

        if not payment or not payment.execute({"payer_id": PayerID}):
            return Response(payment.error)

        order.payment_method = models.order.order.PAYMENT_METHOD_PAYPAL
        order.checkout_details[models.order.order.PAYMENT_METHOD_PAYPAL] = request.data
        order.history[models.order.order.PAYMENT_METHOD_PAYPAL]={
            "action": "pay",
            "time": pendulum.now("UTC").to_iso8601_string()
        }
        order.paid_at = datetime.utcnow()
        #payment status update
        order.payment_status = models.order.order.PAYMENT_STATUS_PAID
        #delivery status update
        lib.helper.delivery_helper.DeliveryHelper.update_delivery_status(**{ "order_oid": order_oid, "order": order, "extra_data": {}, "create_order": True})

        #wallet
        update_wallet(order)

        subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
        content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)
        jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
        
        #order status update
        lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)
        return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/order/{order_oid}/confirmation')

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
    
    @action(detail=False, methods=['GET'], url_path=r"pay_mongo/gateway")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_pay_mongo_gateway(self, request):
        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)
        secret_key = campaign.meta_payment.get("pay_mongo",{}).get("secret")
        
        response = service.pay_mongo.pay_mongo.retrieve_webhook(secret_key)
        if response.status_code != 200:
            order.history[models.order.order.PAYMENT_METHOD_PAYMONGO]={
                "action": "retrieve_webhook",
                "error": response.json()['errors'],
                "time": pendulum.now("UTC").to_iso8601_string()
            }
            order.save()
            raise lib.error_handle.error.api_error.ApiCallerError("choose_another_payment_method")
        
        webhook_exists = False
        webhook_url = f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/pay_mongo/webhook/'
        webhook_list = [ value for list_data in response.json()['data'] for key, value in list_data['attributes'].items() if key == 'url']
        if webhook_url in webhook_list:
            webhook_exists = True
        # print(webhook_list)
        if not webhook_exists:
            response = service.pay_mongo.pay_mongo.register_webhook(secret_key, webhook_url)
            if response.status_code != 200:
                order.history[models.order.order.PAYMENT_METHOD_PAYMONGO]={
                    "action": "register_webhook",
                    "error": response.json()['errors'],
                    "time": pendulum.now("UTC").to_iso8601_string()
                }
                order.save()
                raise lib.error_handle.error.api_error.ApiCallerError("choose_another_payment_method")

        payment_amount = lib.helper.payment_helper.transform_payment_amount(order.total, campaign.decimal_places, campaign.price_unit)
        response = service.pay_mongo.pay_mongo.create_link(order_oid, payment_amount, secret_key)
        if response.status_code != 200:
            order.history[models.order.order.PAYMENT_METHOD_PAYMONGO]={
                "action": "create_link",
                "error": response.json()['errors'],
                "time": pendulum.now("UTC").to_iso8601_string()
            }
            order.save()
            raise lib.error_handle.error.api_error.ApiCallerError("choose_another_payment_method")
        payMongoResponse = json.loads(response.text)
        print(payMongoResponse)
        return Response(payMongoResponse['data']['attributes']['checkout_url'], status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r"pay_mongo/webhook")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def pay_mongo_webhook_paid(self, request):
        print(request.data)
        order_oid = int(request.data['data']['attributes']['data']['attributes']['description'].split('_')[1])
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        if (request.data['data']['attributes']['data']['attributes']['status'] == 'paid'):
            
            order.payment_method = models.order.order.PAYMENT_METHOD_PAYMONGO
            order.checkout_details[models.order.order.PAYMENT_METHOD_PAYMONGO] = request.data
            order.history[models.order.order.PAYMENT_METHOD_PAYMONGO]={
                "action": "pay",
                "time": pendulum.now("UTC").to_iso8601_string()
            }
            order.paid_at = datetime.utcnow()
            #payment status update
            order.payment_status = models.order.order.PAYMENT_STATUS_PAID
            #delivery status update
            lib.helper.delivery_helper.DeliveryHelper.update_delivery_status(**{ "order_oid": order_oid, "order": order, "extra_data": {}, "create_order": True})
            

            #wallet
            update_wallet(order)

            subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=order.campaign.lang)
            content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, order.campaign, lang=order.campaign.lang)
            jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
            
        #order status update
        lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)
        return Response('response', status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r"ecpay/credential")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_ecpay_credential(self, request):

        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)

        merchant_id = campaign.meta_payment.get("ecpay",{}).get("merchant_id")
        hash_key = campaign.meta_payment.get("ecpay",{}).get("hash_key")
        hash_iv = campaign.meta_payment.get("ecpay",{}).get("hash_iv")
        
        payment_amount = lib.helper.payment_helper.transform_payment_amount(order.total, campaign.decimal_places, campaign.price_unit)


        action,payment = service.ecpay.ecpay.create_order(merchant_id, hash_key, hash_iv, int(payment_amount) , order, 
            f'{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/ecpay/callback/success/{order_oid}/', 
            f'{settings.WEB_SERVER_URL}/buyer/order/{order_oid}/confirmation'
            )
        
        if not payment:
            raise lib.error_handle.error.api_error.ApiCallerError('choose_another_payment_method')

        
        return Response({'action':action,'data':payment})
        
        # raise lib.error_handle.error.api_error.ApiCallerError('Payment Error, Please Choose Another Payment Method')
    
    @action(detail=False, methods=['POST'], url_path=r"ecpay/callback/success/(?P<order_oid>[^/.]+)",parser_classes=(FormParser,), renderer_classes = (StaticHTMLRenderer,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def ecpay_success_callback(self, request,order_oid):
        
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = order.campaign
        merchant_id = campaign.meta_payment.get("ecpay",{}).get("merchant_id")
        hash_key = campaign.meta_payment.get("ecpay",{}).get("hash_key")
        hash_iv = campaign.meta_payment.get("ecpay",{}).get("hash_iv")
        
        payment_res = request.data.dict()
        
        check_value = service.ecpay.ecpay.check_mac_value(merchant_id, hash_key, hash_iv, payment_res)
        
        
        if not payment_res or payment_res['CheckMacValue'] != check_value :
            return print('order is not match')
        
        # {'AlipayID': [''], 
        # 'AlipayTradeNo': [''], 
        # 'amount': ['620'], 
        # 'ATMAccBank': [''], 
        # 'ATMAccNo': [''], 
        # 'auth_code': ['777777'], 
        # 'card4no': ['2222'], 
        # 'card6no': ['431195'], 
        # 'CustomField1': [''], 
        # 'CustomField2': [''], 
        # 'CustomField3': [''], 
        # 'CustomField4': [''], 
        # 'eci': ['0'], 
        # 'ExecTimes': [''], 
        # 'Frequency': [''], 
        # 'gwsr': ['12084016'], 
        # 'MerchantID': ['2000132'], 
        # 'MerchantTradeNo': ['32963'], 
        # 'PayFrom': [''], 
        # 'PaymentDate': ['2022/08/12 10:21:28'], 
        # 'PaymentNo': [''], 
        # 'PaymentType': ['Credit_CreditCard'], 
        # 'PaymentTypeChargeFee': ['12'], 
        # 'PeriodAmount': [''],
        # 'PeriodType': [''], 
        # 'process_date': ['2022/08/12 10:21:28'], 
        # 'red_dan': ['0'], 'red_de_amt': ['0'], 
        # 'red_ok_amt': ['0'], 'red_yet': ['0'], 
        # 'RtnCode': ['1'], 'RtnMsg': ['交易成功'], 
        # 'SimulatePaid': ['0'], 'staed': ['0'], 
        # 'stage': ['0'], 'stast': ['0'], 
        # 'StoreID': [''], 
        # 'TenpayTradeNo': [''], 
        # 'TotalSuccessAmount': [''], 
        # 'TotalSuccessTimes': [''], 
        # 'TradeAmt': ['620'], 
        # 'TradeDate': ['2022/08/12 10:21:04'], 
        # 'TradeNo': ['2208121021044275'], 
        # 'WebATMAccBank': [''], 
        # 'WebATMAccNo': [''], 
        # 'WebATMBankName': [''], 
        # 'CheckMacValue': ['9D8011AE1ADC9F13854745CA88F8DA4DF14B111580EF7AACD29631E034CDC9AA']}
        
        

        if payment_res['RtnCode'] == '0':
            raise lib.error_handle.error.api_error.ApiVerifyError('payment not successful',payment_res['RtnMsg'])
        
        if order.campaign.meta_payment['ecpay']['invoice_enabled']:
            invoice = service.ecpay.ecpay.order_create_invoice(merchant_id, hash_key, hash_iv, order,int(payment_res['amount']))
            order.meta['InvoiceNumber'] = invoice['InvoiceNumber']
        
        order.payment_method = models.order.order.PAYMENT_METHOD_ECPAY
        order.checkout_details[models.order.order.PAYMENT_METHOD_ECPAY] = payment_res
        order.history[models.order.order.PAYMENT_METHOD_ECPAY]={
            "action": "pay",
            "time": pendulum.now("UTC").to_iso8601_string()
        }
        order.paid_at = datetime.utcnow()
        #payment status update
        order.payment_status = models.order.order.PAYMENT_STATUS_PAID
        #delivery status update
        lib.helper.delivery_helper.DeliveryHelper.update_delivery_status(**{ "order_oid": order_oid, "order": order, "extra_data": {}, "create_order": True})
        

        #wallet
        update_wallet(order)

        subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
        content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)
        jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
        # return HttpResponseRedirect(redirect_to=f'{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}/confirmation')
        res = '1|OK'
        
        #order status update
        lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)
        
        return Response(res)
    
    @action(detail=False, methods=['GET'], url_path=r"rapyd/gateway")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_rapyd_gateway(self, request):

        order_oid, = lib.util.getter.getparams(request,('order_oid',),with_user=False) 
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)

        access_key = campaign.meta_payment.get("rapyd",{}).get("access_key")
        secret_key = campaign.meta_payment.get("rapyd",{}).get("secret_key")
        country = campaign.meta_payment.get("rapyd",{}).get("country")
        currency = campaign.meta_payment.get("rapyd",{}).get("currency")
        checkout_time = pendulum.now("UTC").to_iso8601_string()
        data = service.rapyd.models.checkout.CreateCheckoutModel(
            amount = order.total, 
            country = country, 
            currency = currency,
            # requested_currency = "TWD",
            # custom_elements = {
            #     "dynamic_currency_conversion": True
            # },
            complete_checkout_url = f"{settings.GCP_API_LOADBALANCER_URL}/api/v2/payment/rapyd/callback/success?order_oid={str(order_oid)}&checkout_time={checkout_time}",
            cancel_checkout_url = f'{settings.WEB_SERVER_URL}/buyer/order/{str(order_oid)}/payment',
            payment_method_type_categories = ["bank_transfer", "card"],
            metadata = {
                "order_oid": order_oid
            },
            # fixed_side = "buy"
        )
        rapyd_service = service.rapyd.rapyd.RapydService(access_key=access_key, secret_key=secret_key)

        api_response = rapyd_service.create_checkout(data)
        
        if api_response.status_code != 200:
            error_message = service.rapyd.rapyd.RapydService.get_error_message(api_response)
            raise lib.error_handle.error.api_error.ApiCallerError(error_message)
        data = api_response.json()
        result = service.rapyd.models.checkout.CheckoutModel(**data["data"])
        order.history[f'{models.order.order.PAYMENT_METHOD_RAPYD}_{checkout_time}']={
            "id":result.id,
            "action": "checkout",
            "time": checkout_time
        }
        order.save()
        return Response(result.redirect_url, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'rapyd/callback/success',)
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def rapyd_success_callback(self, request):
        print("rapyd_success_callback")
        rapyd_status_map = {
            "ACT": "Active and awaiting completion of 3DS or capture. Can be updated.",
            "CAN": "Canceled by the client or the customer's bank.",
            "CLO": "Closed and paid.",
            "ERR": "Error. An attempt was made to create or complete a payment, but it failed.",
            "EXP": "The payment has expired.",
            "NEW": "Not closed.",
            "REV": "Reversed by Rapyd. See cancel_reason, above."
        }
        order_oid, checkout_time = lib.util.getter.getparams(request, ('order_oid', 'checkout_time'), with_user=False)

        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = order.campaign
        
        access_key = campaign.meta_payment.get("rapyd",{}).get("access_key")
        secret_key = campaign.meta_payment.get("rapyd",{}).get("secret_key")

        rapyd_service = service.rapyd.rapyd.RapydService(access_key=access_key, secret_key=secret_key)

        checkout_id = order.history[f'{models.order.order.PAYMENT_METHOD_RAPYD}_{checkout_time}']['id']
        api_response = rapyd_service.retrieve_checkout(checkout_id)
        response_data = api_response.json()
        payment_data = response_data.get('data',{}).get('payment', {})
        payment_status = payment_data.get("status", False)
        order.meta[models.order.order.PAYMENT_METHOD_RAPYD] = response_data
        order.payment_method = models.order.order.PAYMENT_METHOD_RAPYD
        order.checkout_details[models.order.order.PAYMENT_METHOD_RAPYD] = {
            "payment_status_description": rapyd_status_map[payment_status],
            **payment_data
        }
        callback_time = pendulum.now("UTC").to_iso8601_string()
        order.history[f"{models.order.order.PAYMENT_METHOD_RAPYD}_{callback_time}"]={
            "action": "checkout_success_callback",
            "time": callback_time
        }
        if payment_status == "CLO":
            order.paid_at = datetime.utcnow()
            order.payment_status = models.order.order.PAYMENT_STATUS_PAID
            #delivery status update
            lib.helper.delivery_helper.DeliveryHelper.update_delivery_status(**{ "order_oid": order_oid, "order": order, "extra_data": {}, "create_order": True})
            #wallet
            update_wallet(order)

            subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
            content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)
            jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
            return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/order/{order_oid}/confirmation')
        elif payment_status == "ACT":
            order.payment_status = models.order.order.PAYMENT_STATUS_AWAITING_CONFIRM
        elif payment_status == "EXP":
            order.payment_status = models.order.order.PAYMENT_STATUS_EXPIRED
        
        #order status update
        lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)
        
        return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/order/{order_oid}')
    
    
    
    @action(detail=False, methods=['POST'], url_path=r"rapyd/webhook")
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_rapyd_webhook(self, request):
        order = None
        try:
            callback_time = pendulum.now("UTC").to_iso8601_string()
            order.history[f"{models.order.order.PAYMENT_METHOD_RAPYD}_{callback_time}"]={
                "action": "webhook",
                "time": callback_time,
                "data": body
            }
            
            signature = request.headers['Signature']
            http_uri = settings.GCP_API_LOADBALANCER_URL+request.get_full_path()
            salt = request.headers['Salt']
            timestamp = request.headers['Timestamp']
            
            body = json.loads(request.body)
            id = body['id']
            type = body['type']
            data = body['data']
            
            order_oid = data.get("metadata", {}).get("order_oid", "")
            order = lib.util.verify.Verify.get_order_with_oid(order_oid)
            
            campaign = lib.util.verify.Verify.get_campaign_from_order(order)
            access_key = campaign.meta_payment.get("rapyd",{}).get("access_key")
            secret_key = campaign.meta_payment.get("rapyd",{}).get("secret_key")
            
            rapyd_service = service.rapyd.rapyd.RapydService(access_key=access_key, secret_key=secret_key)
            
            if not rapyd_service.auth_webhook_request(signature, http_uri, salt, timestamp, body):
                raise lib.error_handle.error.api_error.ApiCallerError("signature not valid")
            if type == "PAYMENT_FAILED":
                order_status = models.order.order.STATUS_REVIEW
            elif type == "PAYMENT_COMPLETED":
                order.paid_at = datetime.utcnow()
                #payment status update
                order.payment_status = models.order.order.PAYMENT_STATUS_PAID
                #delivery status update
                lib.helper.delivery_helper.DeliveryHelper.update_delivery_status(**{ "order_oid": order_oid, "order": order, "extra_data": {}, "create_order": True})

                #wallet
                update_wallet(order)

                subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
                content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)
                jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
                
            #order status update
            lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)
        except Exception:
            if order:
                order.save()
            print(traceback.format_exc())
        return Response("OK", status=status.HTTP_200_OK)
        

def update_wallet(order):
    point_discount_processor_class:factory.point_discount.PointDiscountProcessor = factory.point_discount.get_point_discount_processor_class(order.campaign.user_subscription)
    point_discount_processor = point_discount_processor_class(order.buyer, order.campaign.user_subscription, None, order.campaign.meta_point, points_earned = order.points_earned)
    point_discount_processor.create_point_transaction(order_id = order.id)
    point_discount_processor.update_wallet()