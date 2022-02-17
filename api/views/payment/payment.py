import urllib

import stripe
from django.shortcuts import redirect
from rest_framework import views, viewsets, status
import paypalrestsdk, json
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import views, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

from api.utils.common.common import getdata, getparams
from api.models.order.order import Order
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile
import pendulum, time, datetime

from django.http import HttpResponseRedirect
from api.utils.common.verify import Verify
from api.views.payment._payment import HitPay_Helper
from backend.pymongo.mongodb import db
from mail.sender.sender import *

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.error_handle.error.api_error import ApiVerifyError

import hmac, hashlib, base64, binascii
from backend.i18n.payment_comfirm_mail import i18n_get_mail_content, i18n_get_mail_subject
from api.utils.error_handle.error_handler.email_error_handle import email_error_handler
from mail.sender.sender import send_smtp_mail
from django.shortcuts import redirect



platform_dict = {'facebook':FacebookPage, 'youtube':YoutubeChannel, 'instagram':InstagramProfile}


@email_error_handler
def send_email(order_id):
    order_data = db.api_order.find_one({'id': int(order_id)})
    campaign_id = order_data['campaign_id']
    campaign_data = db.api_campaign.find_one({'id': int(campaign_id)})
    facebook_page_id = campaign_data['facebook_page_id']
    shop_name = db.api_facebook_page.find_one({'id': int(facebook_page_id)})['name']
    customer_email = order_data['shipping_email']

    mail_subject = i18n_get_mail_subject(shop_name)
    mail_content = i18n_get_mail_content(order_id, campaign_data, order_data, shop_name)

    send_smtp_mail(customer_email, mail_subject, mail_content)


class PaymentViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'get_ipg_order_data', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_ipg_order_data(self, request, pk=None):

        order_id = request.query_params.get('order_id')

        order = Verify.get_order(order_id)

        if not order.platform in platform_dict:
            raise ApiVerifyError("platform not supported")

        platform_class = platform_dict.get(order.platform)

        if not platform_class.objects.filter(id=order.platform_id).exists():
            raise ApiVerifyError("no platform found")
        platform = platform_class.objects.get(id=order.platform_id)

        user_subscriptions = platform.user_subscriptions.all()

        if not user_subscriptions:
            raise ApiVerifyError("platform not in any user_subscription")
        user_subscription = user_subscriptions[0]

        firstdata = user_subscription.meta_payment.get('firstdata')


        #TODO  取campaign meta_payment

        if not firstdata:
            raise ApiVerifyError('no firstdata credential')

        txndatetime = datetime.datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
        chargetotal = order.total
        currency = firstdata['ipg_currency']
        storename = firstdata['ipg_storeId']
        timezone = firstdata['ipg_timezone']
        secret = firstdata['ipg_sharedSecret']


        credential = {
            "chargetotal" : chargetotal,
            # "checkoutoption" : "combinedpage",
            "currency" : currency,
            "hash_algorithm" : "SHA1",
            "mode" : "payonly",

            # "paymentMethod" :"M",
            # "responseFailURL" : settings.GCP_API_LOADBALANCER_URL + f"/api/payment/ipg_payment_fail?order_id={order_id}",
            # "responseSuccessURL" : settings.GCP_API_LOADBALANCER_URL + f"/api/payment/ipg_payment_success?order_id={order_id}",

            "storename" : storename,
            "timezone" : timezone,
            "txndatetime" : txndatetime,
            "txntype" : "sale",
            
        }

        stringToHash = str(storename) + str(txndatetime) + str(chargetotal) + str(currency) + str(secret)

        ascii = binascii.b2a_hex(stringToHash.encode('utf-8'))   
        # ascii = binascii.b2a_base64()
        # ascii = binascii.b2a_uu()
        hash_object = hashlib.sha1(ascii)
        hex_dig = hash_object.hexdigest()

        credential['hash']= hex_dig

        return Response({"url":"https://test.ipg-online.com/connect/gateway/processing","credential":credential}, status=status.HTTP_200_OK)

        # before_hashing_string = "".join([str(value) for key,value in credential.items()])
        # before_hashing_string = "|".join([str(value) for key,value in credential.items()])

        # print(before_hashing_string)
        sharedsecret=firstdata['ipg_sharedSecret']

        print(sharedsecret.encode())
        dig = hmac.new(sharedsecret.encode(), msg=before_hashing_string.encode(), digestmod=hashlib.sha256).digest()
        print(dig)
        print(type(dig))
        hashExtended = base64.b64encode(dig).decode()
        print(hashExtended)
        credential['hashExtended'] = hashExtended                                                                                                                           


        return Response({"url":"https://test.ipg-online.com/connect/gateway/processing","credential":credential}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'ipg_payment_success')
    @api_error_handler
    def ipg_payment_success(self, request):

        order_id, = getparams(request, ('order_id',), with_user=False)
        order = Verify.get_order(order_id)

        order.meta['ipg_success']=request.data
        order.status="complete"
        order.save()

        print(request)
        # return HttpResponseRedirect(redirect_to='https://www.google.com')
        return HttpResponseRedirect(redirect_to=settings.WEB_SERVER_URL+f'/buyer/order/{order.id}/confirmation')

        # ‘response_hash’
        # resopnse code
        # approval_code|chargetotal|currency|txndatetime|storename
        order_id = request.query_params.get('order_id')

        print(f"order_id {order_id}")

        approval_code, oid, refnumber, trancaction_status, txndate_processed, ipgTransactionId, fail_reason, response_hash = getdata(request, ("approval_code", "oid", "refnumber", "status", "txndate_processed", "ipgTransactionId", "fail_reason", "response_hash"))


        print(f"approval_code {approval_code}")
        print(f"oid {oid}")
        print(f"refnumber {refnumber}")
        print(f"trancaction_status {trancaction_status}")
        print(f"txndate_processed {txndate_processed}")
        print(f"ipgTransactionId {ipgTransactionId}")
        print(f"fail_reason {fail_reason}")
        print(f"response_hash {response_hash}")

        return HttpResponseRedirect(redirect_to='https://www.google.com')

    @action(detail=False, methods=['GET'], url_path=r'ipg_payment_fail')
    @api_error_handler
    def ipg_payment_fail(self, request, pk=None):

        order_id, = getparams(request, ('order_id',), with_user=False)
        order = Verify.get_order(order_id)

        order.meta['ipg_fail']=request.data
        order.save()
        
        print(request)
        return HttpResponseRedirect(redirect_to=settings.WEB_SERVER_URL+f'/buyer/order/{order.id}/confirmation')
        approval_code, oid, refnumber, trancaction_status, approval_code, txndate_processed, ipgTransactionId, fail_reason, response_hash = getdata(request, ("approval_code", "oid", "refnumber", "status", "approval_code", "txndate_processed", "ipgTransactionId", "fail_reason", "response_hash"))


        # OrderMetaModel::api_update($order_id, 'payment_info', $request->post('ipgTransactionId'));
        # OrderMetaModel::api_update($order_id, 'payment_info_ccbrand', $request->post('ccbrand'));
        # OrderMetaModel::api_update($order_id, 'payment_info_cardnumber', $request->post('cardnumber'));
        # OrderMetaModel::api_update($order_id, 'payment_method', 'First Data IPG');

        # (new OrderController)->checkout_process($campaign_id, $fb_psid, $order_id);
        # (new EmailController)->send_order($order_id);
        # return redirect()->route('page_confirmation', ['campaign_id' => $campaign_id, 'order_id' => $order_id]);


        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def direct_payment(self, request, *args, **kwargs):
        platform_name = request.GET["platform_name"]
        platform_id = request.GET["platform_id"]
        return Response({
            'platform_name': platform_name,
            'platform_id': platform_id
        })

    @action(detail=False, methods=['GET'], url_path=r"paypal_payment_create", permission_classes=(IsAuthenticated,))
    def paypal_payment_create(self, request, *args, **kwargs):
        """

        Args:
            request:
            *args:
            **kwargs:

        Returns: json: {
            "status": 202,
            "approval_url": approval_url
        }

        """
        api_user, order_id = getparams(
            request, ("order_id",), seller=False)
        # customer_user = Verify.get_customer_user(request)
        order_object = Verify.get_order(order_id)

        amount = order_object.total
        campaign_obj = order_object.campaign
        currency = campaign_obj.meta_payment["sg"]["paypal"]["paypal_currency"]
        if not currency:
            currency = 'SGD' if not order_object.currency else order_object.currency

        # data is json, example:
        data = [{
            "item_list": {
                # "items": [
                #     {
                #         # "name": "Cake",
                #         # "price": "8.00",
                #         "currency": currency,
                #         # "quantity": 1
                #     }
                # ]
            },
            "amount": {
                "total": amount,
                "currency": currency},
            "description": "This is the payment transaction description."
        }]
        # 之前寫死
        # paypalrestsdk.configure({
        #     "mode": settings.PAYPAL_CONFIG["mode"],
        #     "client_id": settings.PAYPAL_CONFIG["client_id"],
        #     "client_secret": settings.PAYPAL_CONFIG["client_secret"]
        # })
        paypalrestsdk.configure({
            "mode": "sandbox",  # live
            "client_id": campaign_obj.meta_payment["sg"]["paypal"]["paypal_clientId"],
            "client_secret": campaign_obj.meta_payment["sg"]["paypal"]["paypal_secret"]
        })
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": f"{settings.GCP_API_LOADBALANCER_URL}/api/payment/paypal_payment_complete_check?order_id={order_id}",
                "cancel_url": f"{settings.WEB_SERVER_URL}/payment/cancel"
            },
            "transactions": data
        })
        if payment.create():
            print("Payment created successfully")
        else:
            print(payment.error)
            return Response(payment.error)

        for link in payment.links:
            if link.rel == "approval_url":
                # Convert to str to avoid Google App Engine Unicode issue
                # https://github.com/paypal/rest-api-sdk-python/pull/58
                approval_url = str(link.href)
                print("Redirect for approval: %s" % (approval_url))
                return Response({
                    "status": 202,
                    "approval_url": approval_url
                })
        return Response({
            "approval_url": ""
        })

    @action(detail=False, methods=['GET'], url_path=r"paypal_payment_complete_check")
    def paypal_payment_complete_check(self, request, *args, **kwargs):

        paymentId = request.GET["paymentId"]
        payer_id = request.GET["PayerID"]
        order_id = request.GET["order_id"]
        order_object = Verify.get_order(order_id)
        campaign_obj = order_object.campaign

        paypalrestsdk.configure({
            "mode": "sandbox",  # live
            "client_id": campaign_obj.meta_payment["sg"]["paypal"]["paypal_clientId"],
            "client_secret": campaign_obj.meta_payment["sg"]["paypal"]["paypal_secret"]
        })

        payment = paypalrestsdk.Payment.find(paymentId)
        if payment.execute({"payer_id": payer_id}):
            print("Payment execute successfully")
            order_object.status = "complete"
            order_object.save()
            return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/order/{order_object.id}/confirmation')
        else:
            print(payment.error)  # Error Hash
            return Response(payment.error)


    # @action(detail=False, methods=['GET'], url_path=r'get_ipg_order_data')
    # @api_error_handler
    # def get_ipg_order_data(self, request, pk=None):
    #     api_user, order_id = getparams(
    #         request, ("order_id", ), seller=False)

    #     if not api_user:
    #         raise ApiVerifyError("no user found")
    #     elif api_user.status != "valid":
    #         raise ApiVerifyError("not activated user")

    #     _, _, pre_order = verify_seller_request(
    #         api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

    #     serializer = PreOrderSerializer(pre_order)

    #     return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'hit_pay', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def hit_pay(self, request):
        api_user, order_id = getparams(
            request, ("order_id", ))

        user_data = db.api_user.find_one({'id': api_user.id})
        name = user_data['name']
        email = user_data['email']
        order_data = db.api_order.find_one({'id': int(order_id)})
        if not order_data:
            raise ApiVerifyError('no order found')
        currency = 'SGD' if not order_data['currency'] else order_data['currency']
        amount = order_data['total']

        # params = {
        #     'email': email,
        #     'name': name,
        #     'redirect_url': 'https://v1login.liveshowseller.com/buyer/order/' + order_id + '/confirmation',
        #     'webhook': 'https://gipassl.algotech.app/api/payment/hit_pay_webhook/',
        #     'amount': amount,
        #     'currency': currency,
        #     'reference_number': order_id,
        # }
        headers = {
            'X-BUSINESS-API-KEY': settings.HITPAY_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
        params = {
            'email': email,
            'name': name,
            'redirect_url': f'{settings.GCP_API_LOADBALANCER_URL}/api/payment/hit_pay_return_redirect/?order_id={order_id}',
            'webhook': f'{settings.GCP_API_LOADBALANCER_URL}/api/payment/hit_pay_webhook/',
            'amount': amount,
            'currency': currency,
            'reference_number': order_id,
        }
        
        code, ret = HitPay_Helper.HitPayApiCaller(headers=headers,
                            params=params).post()
        print (code, ret)

        if code != 201:
            raise Exception('hitpay got wrong')
        #TODO record payment not replace   

        return Response(ret['url'])

    @action(detail=False, methods=['POST'], url_path=r'hit_pay_webhook', parser_classes=(MultiPartParser, FormParser))
    def hit_pay_webhook(self, request):
        data_dict = request.data.dict()
        payment_id, payment_request_id, phone = data_dict['payment_id'], data_dict['payment_request_id'], data_dict['phone']
        amount, currency, status = data_dict['amount'], data_dict['currency'], data_dict['status']
        order_id = data_dict['reference_number']
        _hmac, secret_salt = data_dict['hmac'], settings.HITPAY_SECRET_SALT
        sort_key_list = ['amount', 'currency', 'hmac', 'payment_id', 'payment_request_id', 'phone', 'reference_number', 'status']

        hitpay_dict, info_dict = {}, {}
        info_dict['payment_id'] = payment_id
        info_dict['payment_request_id'] = payment_request_id
        hitpay_dict['hitpay'] = info_dict
        total = int(db.api_order.find_one({'id': int(order_id)})['total'])

        #TODO change to real checking way
        if status == 'completed' and int(total) == int(float(amount)):
            db.api_order.update_one(
                { 'id': int(order_id) },
                { '$set': {'status': 'complete', 'checkout_details': hitpay_dict, 'payment_method': 'hitpay'} }
            )

        send_email(order_id)
        return Response('hitpay succed')
    
    @action(detail=False, methods=['GET'], url_path=r'hit_pay_return_redirect')
    @api_error_handler
    def hit_pay_redirect(self, request):
        time.sleep(2)
        order_id, status = request.query_params.get('order_id'), ''
        payment_request_id = db.api_order.find_one({'id': int(order_id)})['checkout_details']['hitpay']['payment_request_id']

        headers = {
            'X-BUSINESS-API-KEY': settings.HITPAY_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
        params = {
            'ID': payment_request_id
        }
        code, ret = HitPay_Helper.HitPayApiCaller(headers=headers, params=params).get()
        #TODO return redirect to order history page
        if code != 200:
            raise Exception('hitpay get payment request api failed')
        
        for _ret in ret:
            if _ret['id'] == payment_request_id:
                status = _ret['status']
        if status == 'completed':
            return redirect('https://v1login.liveshowseller.com/buyer/order/' + order_id + '/confirmation')
        #TODO else return redirect to order history page


    @action(detail=False, methods=['PUT'], url_path=r'buyser_receipt_upload', parser_classes=(MultiPartParser,))
    @api_error_handler
    def buyser_receipt_upload(self, request):
        image = request.data["image"]
        print(f"image: {image}")
        # if not image:
        #     raise ApiVerifyError("no image found")
        order_id = request.data["order_id"]
        last_five_digit = request.data["last_five_digit"]
        print(f"order_id: {order_id}")
        print(f"last_five_digit: {last_five_digit}")
        if not Order.objects.filter(id=order_id).exists():
            raise ApiVerifyError("no order found")

        order = Order.objects.get(id=order_id)
        api_user = Order.objects.get(id=order_id).campaign.created_by
        print(api_user)
        platform_name = order.platform
        print(f"platform_name: {platform_name}")
        platform_id = order.platform_id
        print(f"platform_id: {platform_id}")
        # _, user_subscription = verify_request(
        #     api_user, platform_name, platform_id)

        order.meta["receipt_image"] = ""
        order.meta["last_five_digit"] = ""
        if image != "undefined":
            image_path = default_storage.save(
                f'campaign/{order.campaign.id}/order/{order.id}/receipt/{image.name}', ContentFile(image.read()))
            image_path = settings.GS_URL + image_path
            order.meta["receipt_image"] = image_path
        if last_five_digit:
            order.meta["last_five_digit"] = last_five_digit
        order.payment_method = "Direct Payment"
        order.status = "complete"
        order.save()
        send_email(order_id)

        return Response({"message": "upload succeed"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'get_direct_payment_info')
    @api_error_handler
    def get_direct_payment_info(self, request):
        try:
            api_user, order_id = getparams(request,('order_id',), seller=False)
            if not Order.objects.filter(id=order_id).exists():
                raise ApiVerifyError("no order found")

            order = Verify.get_order(order_id)
            Verify.user_match_order(api_user, order)
            meta_payment = order.campaign.meta_payment
            meta_payment = json.loads(json.dumps(meta_payment))
            return Response(meta_payment, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path=r'stripe_pay', parser_classes=(FormParser,))
    @api_error_handler
    def stripe_pay_create_checkout_session(self, request):
        # stripe.api_key = settings.STRIPE_API_KEY
        try:
            # api_user, order_id = getparams(
            #     request, ("order_id",), seller=False)
            # customer_user = Verify.get_customer_user(request)
            order_id = request.data["order_id"]
            order_object = Verify.get_order(order_id)
            campaign = order_object.campaign
            stripe.api_key = campaign.meta_payment.get("sg").get("stripe").get("stripe_secret")
            print("stripe.api_key", stripe.api_key)
            currency = "SGD" if order_object.currency is None else order_object.currency
            item_list = []
            for key, values in order_object.products.items():
                image = urllib.parse.quote(f"{settings.GS_URL}{values.get('image', '')}")
                print(image)
                product = stripe.Product.create(
                    name=values.get("name", ""),
                    images=[image]
                )
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(values.get("price", 0)*100),
                    currency=currency,
                )
                item_list.append(
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price': price.id,
                        "quantity": values.get("qty", 0)
                    },
                )
            print(item_list)
            discounts = []
            if order_object.adjust_price:
                discount = stripe.Coupon.create(
                    amount_off=int(-order_object.adjust_price * 100),
                    currency=currency
                )
                discounts.append(
                    {
                        'coupon': discount.id,
                    }
                )
            stripe.Coupon.create(percent_off=20, duration="once")
            shipping_options = []
            if order_object.shipping_cost:
                shipping_rate = stripe.ShippingRate.create(
                    display_name="General Shipping",
                    type="fixed_amount",
                    fixed_amount={
                        'amount': int(order_object.shipping_cost * 100),
                        'currency': currency,
                    }
                )
                shipping_options.append(
                    {
                        'shipping_rate': shipping_rate.id,
                    }
                )
            elif order_object.free_delivery:
                shipping_rate = stripe.ShippingRate.create(
                    display_name="Free Delivery",
                    type="fixed_amount",
                    fixed_amount={
                        'amount': 0,
                        'currency': currency,
                    }
                )
                shipping_options.append(
                    {
                        'shipping_rate': shipping_rate.id,
                    }
                )
            checkout_session = stripe.checkout.Session.create(
                line_items=item_list,
                shipping_options=shipping_options,
                discounts=discounts,
                mode='payment',
                success_url=settings.GCP_API_LOADBALANCER_URL + '/api/payment/strip_success?session_id={CHECKOUT_SESSION_ID}&order_id=' + str(order_object.id),
                cancel_url=f"{settings.WEB_SERVER_URL}/payment/cancel",

            )
            print(checkout_session.url)
            return Response(checkout_session.url, status=status.HTTP_303_SEE_OTHER)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path=r'strip_success',)
    @api_error_handler
    def strip_success(self, request):
        try:
            # stripe.api_key = settings.STRIPE_API_KEY
            print("session_id", request.GET["session_id"])
            order_id = request.GET["order_id"]
            order_object = Verify.get_order(order_id)
            campaign_object = order_object.campaign
            stripe.api_key = campaign_object.meta_payment.get("sg").get("stripe").get("stripe_secret")
            print("stripe.api_key", stripe.api_key)
            session = stripe.checkout.Session.retrieve(request.GET["session_id"])
            payment_intent = stripe.PaymentIntent.retrieve(
                session.payment_intent,
            )
            print("datetime", datetime.datetime.fromtimestamp(payment_intent.created))
            if payment_intent.status == "succeeded":
                checkout_details = {
                    "client_secret": payment_intent.client_secret,
                    "created": datetime.datetime.fromtimestamp(payment_intent.created),
                    "id": payment_intent.id,
                    "object": payment_intent.object,
                    "receipt_email": payment_intent.receipt_email,
                    "receipt_url": payment_intent.charges.data[0].receipt_url,
                }
                db.api_order.update_one(
                    {'id': int(order_object.id)},
                    {'$set': {'status': 'complete', 'checkout_details': checkout_details, 'payment_method': 'Stripe'}}
                )
            return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/buyer/order/{order_object.id}/confirmation')
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


