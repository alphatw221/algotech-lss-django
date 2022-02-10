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
from api.models.user import user
from api.models.user.user_subscription import UserSubscription
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
import pendulum, time, datetime

from django.http import HttpResponseRedirect
from api.models.user.user_subscription import UserSubscriptionSerializerMeta
from api.utils.common.verify import Verify
from api.views.payment._payment import HitPay_Helper
from api.views.user.user_subscription import verify_request
from backend.pymongo.mongodb import db
from mail.sender.sender import *

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.error_handle.error.api_error import ApiVerifyError
106

import hmac, hashlib, base64, binascii
from backend.i18n.payment_comfirm_mail import i18n_get_mail_content, i18n_get_mail_subject
from api.utils.error_handle.error_handler.email_error_handle import email_error_handler
from mail.sender.sender import send_smtp_mail



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
        currency = 'SGD' if not order_object.currency else order_object.currency
        # currency = campaign_obj.meta_payment["sg"]["paypal"]["paypal_currency"]

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
        # sanbox mode
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_CONFIG["mode"],
            "client_id": settings.PAYPAL_CONFIG["client_id"],
            "client_secret": settings.PAYPAL_CONFIG["client_secret"]
        })
        # live mode
        # paypalrestsdk.configure({
        #     "mode": "live",
        #     "client_id": campaign_obj.meta_payment["sg"]["paypal"]["paypal_clientId"],
        #     "client_secret": campaign_obj.meta_payment["sg"]["paypal"]["paypal_secret"]
        # })
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": settings.PAYPAL_CONFIG["complete_url"] + f"?order_id={order_id}",
                "cancel_url": f"{settings.LOCAL_API_SERVER}/buyer/order/{order_id}/confirmation"
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

        # sandbox mode
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_CONFIG["mode"],
            "client_id": settings.PAYPAL_CONFIG["client_id"],
            "client_secret": settings.PAYPAL_CONFIG["client_secret"]
        })
        # live mode
        # paypalrestsdk.configure({
        #     "mode": "live",
        #     "client_id": campaign_obj.meta_payment["sg"]["paypal"]["paypal_clientId"],
        #     "client_secret": campaign_obj.meta_payment["sg"]["paypal"]["paypal_secret"]
        # })

        payment = paypalrestsdk.Payment.find(paymentId)
        if payment.execute({"payer_id": payer_id}):
            print("Payment execute successfully")
            order_object.status = "complete"
            order_object.save()
            return HttpResponseRedirect(f"http://localhost:8000/buyer/order/{order_object.id}/confirmation")
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

        params = {
            'email': email,
            'name': name,
            'redirect_url': 'https://v1login.liveshowseller.com/buyer/order/' + order_id + '/confirmation',
            'webhook': 'https://gipassl.algotech.app/api/payment/hit_pay_webhook/',
            'amount': amount,
            'currency': currency,
            'reference_number': order_id,
        }
        headers = {
            'X-BUSINESS-API-KEY': '64044c7551b232cbf23b32d9b21e30ff1f4c5b42068c8c59864f161cad6af21b',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
        code, ret = HitPay_Helper.HitPayApiCaller(headers=headers,
                            params=params).post()
        if code != 201:
            raise Exception('hitpay got wrong')
        #TODO record payment not replace   
        db.api_order.find_one () 
        # db.api_order.update_one({'id': int(order_id)}, {'$set': {'meta': {'payment_id': ret['id']}}}) 

        return Response(ret['url'])

    @action(detail=False, methods=['POST'], url_path=r'hit_pay_webhook', parser_classes=(MultiPartParser, FormParser))
    def hit_pay_webhook(self, request):
        data_dict = request.data.dict()
        payment_id = data_dict['payment_id']
        payment_request_id = data_dict['payment_request_id']
        amount = data_dict['amount']
        status = data_dict['status']
        order_id = data_dict['reference_number']
        hmac = data_dict['hmac']
        secret_salt = '2MUizyJj429NIoOMmTXedyICmbwS1rt6Wph7cGqzG99IkmCV6nUCQ22lRVCB0Rgu'

        hitpay_dict, info_dict = {}, {}
        info_dict['payment_id'] = payment_id
        info_dict['payment_request_id'] = payment_request_id
        hitpay_dict['hitpay'] = info_dict
        total = int(db.api_order.find_one({'id': int(order_id)})['total'])

        #TODO change to real checking way
        # if status == 'completed' and float(total) == float(amount):
        db.api_order.update_one(
            { 'id': int(order_id) },
            { '$set': {'status': 'complete', 'checkout_details': hitpay_dict, 'payment_method': 'hitpay'} }
        )

        send_email(order_id)    
        return Response('hitpay succed')


    @action(detail=False, methods=['PUT'], url_path=r'buyser_receipt_upload', parser_classes=(MultiPartParser,))
    @api_error_handler
    def buyser_receipt_upload(self, request):
        meta_data = {
            "last_five_digit": "",
            "receipt_image": ""
        }
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

        send_email(order_id)
        if image != "undefined":
            image_path = default_storage.save(
                f'campaign/{order.campaign.id}/order/{order.id}/receipt/{image.name}', ContentFile(image.read()))
            image_path = settings.GS_URL + image_path
            meta_data["receipt_image"] = image_path
        if last_five_digit:
            meta_data["last_five_digit"] = last_five_digit
        order.meta = meta_data
        order.payment_method = "Direct Payment"
        order.status = "complete"
        order.save()

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


