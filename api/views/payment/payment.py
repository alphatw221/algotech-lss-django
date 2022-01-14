import json

from rest_framework import views, viewsets, status
import paypalrestsdk
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

import datetime
import hashlib
from django.http import HttpResponseRedirect
from api.models.user.user_subscription import UserSubscriptionSerializerMeta
from api.utils.common.common import getparams
from api.views.payment._payment import HitPay_Helper
from api.views.user.user_subscription import verify_request
from backend.pymongo.mongodb import db

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.error_handle.error.api_error import ApiVerifyError

platform_dict = {'facebook':FacebookPage, 'youtube':YoutubeChannel, 'instagram':InstagramProfile}

class PaymentViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'get_ipg_order_data', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_ipg_order_data(self, request, pk=None):

        order_id = request.query_params.get('order_id')

        if not Order.objects.filter(id=order_id).exists():
            raise ApiVerifyError("no order_id found")
        order = Order.objects.get(id=order_id)

        platform_class = platform_dict.get(order.platform, None)

        if not platform_class.objects.filter(id=order.platform_id).exists():
            raise ApiVerifyError("no platform found")
        platform = platform_class.objects.get(id=order.platform_id)
        user_subscriptions = platform.user_subscriptions.all()

        if not user_subscriptions:
            raise ApiVerifyError("platform not in any user_subscription")
        user_subscription = user_subscriptions[0]

        firstdata = user_subscription.meta_payment.get('firstdata')

        if not firstdata:
            raise ApiVerifyError('no firstdata credential')

        firstdata['is_ipg']

        storename = firstdata['ipg_storeId']
        txndatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chargetotal = order.total
        shared_secret = firstdata['ipg_sharedSecret']
        payment_hash=hashlib.sha256((storename + str(txndatetime) + str(chargetotal) + shared_secret).encode('utf-8')).hexdigest()
        currency = firstdata['ipg_currency']

        data={
            "storename":storename,
            "txntype":"sale",
            "mode":"payonly",
            "timezone":firstdata['ipg_timezone'],
            "txndatetime": txndatetime,
            "hash_algorithm":"SHA256",
            "hash":payment_hash,
            "chargetotal":chargetotal,
            "currency":currency,
            "responseSuccessURL":settings.GCP_API_LOADBALANCER_URL + f"/api/payment/ipg_payment_success?order_id={order_id}",
            "responseFailURL":settings.GCP_API_LOADBALANCER_URL + f"/api/payment/ipg_payment_fail?order_id={order_id}"
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'ipg_payment_success')
    @api_error_handler
    def ipg_payment_success(self, request, pk=None):

        print(request)
        return HttpResponseRedirect(redirect_to='https://www.google.com')

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

        print(request)
        return HttpResponseRedirect(redirect_to='https://www.google.com')
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

    @action(detail=False, methods=['POST'], url_path=r"paypal_payment_create")
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

        # get request post data  = request.data
        # data is json, example:
        # [{
        #     "item_list": {
        #         "items": [{
        #             "name": "Cake",
        #             "price": "8.00",
        #             "currency": "SGD",
        #             "quantity": 1}]},
        #     "amount": {
        #         "total": "8.00",
        #         "currency": "SGD"},
        #     "description": "This is the payment transaction description."
        # }]
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_CONFIG["mode"],
            "client_id": settings.PAYPAL_CONFIG["client_id"],
            "client_secret": settings.PAYPAL_CONFIG["client_secret"]
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": settings.PAYPAL_CONFIG["complete_url"],
                "cancel_url": settings.PAYPAL_CONFIG["cancel_url"]
            },
            "transactions": request.data
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
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_CONFIG["mode"],
            "client_id": settings.PAYPAL_CONFIG["client_id"],
            "client_secret": settings.PAYPAL_CONFIG["client_secret"]
        })

        paymentId = request.GET["paymentId"]
        payer_id = request.GET["PayerID"]
        payment = paypalrestsdk.Payment.find(paymentId)

        if payment.execute({"payer_id": payer_id}):
            print("Payment execute successfully")
            return Response({
                "status": 202,
                "message": "Payment execute successfully"
            })
            # return HttpResponseRedirect("https://liveshowseller.com/")
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
    def hit_pay(self, request):
        api_user, order_id = getparams(
            request, ("order_id", ))

        user_data = db.api_user.find_one({'id': api_user.id})
        name = user_data['name']
        email = user_data['email']
        order_data = db.api_order.find_one({'id': int(order_id)})
        currency = order_data['currency']
        amount = order_data['total']

        params = {
            'email': email,
            'name': name,
            'redirect_url': 'https://www.google.com/',
            'webhook': 'http://104.199.211.63/api/payment/hit_pay_webhook/',
            'amount': amount,
            'currency': currency,
            'reference_number': order_id,
        }
        headers = {
            'X-BUSINESS-API-KEY': '64044c7551b232cbf23b32d9b21e30ff1f4c5b42068c8c59864f161cad6af21b',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
        ret = HitPay_Helper.HitPayApiCaller(headers=headers,
                            params=params).post()

        return Response(ret)

    @action(detail=False, methods=['POST'], url_path=r'hit_pay_webhook', parser_classes=(MultiPartParser, FormParser))
    def hit_pay_webhook(self, request):
        # headers = {
        #     'X-BUSINESS-API-KEY': '64044c7551b232cbf23b32d9b21e30ff1f4c5b42068c8c59864f161cad6af21b',
        #     'Content-Type': 'application/x-www-form-urlencoded',
        #     'X-Requested-With': 'XMLHttpRequest'
        # }
        # ret = HitPay_Helper.HitPayApiCaller(f'/{payment_request_id}', headers=headers).get()
        data_dict = request.data.dict()
        payment_id = data_dict['payment_id']
        payment_request_id = data_dict['payment_request_id']
        amount = data_dict['amount']
        status = data_dict['status']
        reference_number = data_dict['reference_number']
        hmac = data_dict['hmac']
        secret_salt = '2MUizyJj429NIoOMmTXedyICmbwS1rt6Wph7cGqzG99IkmCV6nUCQ22lRVCB0Rgu'



        hitpay_dict, info_dict = {}, {}

        info_dict['payment_id'] = payment_id
        info_dict['payment_request_id'] = payment_request_id
        hitpay_dict['hitpay'] = info_dict
        total = int(db.api_order.find_one({'id': int(reference_number)})['total'])

        if status == 'completed' and total == int(amount):
            db.api_order.update_one(
                { 'id': int(reference_number) },
                { '$set': {'status': 'paid', 'checkout_details': hitpay_dict} }
            )

        return Response('request')


    @action(detail=False, methods=['PUT'], url_path=r'buyser_receipt_upload', parser_classes=(MultiPartParser,))
    def buyser_receipt_upload(self, request):
        try:
            image = request.data["image"]
            if not image:
                raise ApiVerifyError("no image found")
            order_id = request.data["order_id"]
            print(f"order_id: {order_id}")
            if not Order.objects.filter(id=order_id).exists():
                raise ApiVerifyError("no order found")

            order = Order.objects.get(id=order_id)

            # api_user = request.user.api_users.get(type='user')
            api_user = user.User.objects.get(id=12)
            print(api_user)
            platform_name = order.platform
            print(f"platform_name: {platform_name}")
            platform_id = order.platform_id
            print(f"platform_id: {platform_id}")
            campaign_id = order.campaign_id

            _, user_subscription = verify_request(
                api_user, platform_name, platform_id)

            image_path = default_storage.save(
                f'{user_subscription.id}/order/{order.id}/receipt/{image.name}', ContentFile(image.read()))
            print(image_path)
            order.image = settings.GS_URL + image_path
            order.save()
            return Response({"message": "upload succeed"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path=r'get_direct_payment_info')
    def get_direct_payment_info(self, request):
        try:
            order_id = request.GET["order_id"]
            if not Order.objects.filter(id=order_id).exists():
                raise ApiVerifyError("no order found")
            meta_payment = Order.objects.get(id=order_id).campaign.meta_payment
            meta_payment = json.loads(json.dumps(meta_payment))
            print(meta_payment)
            data = {
                "is_general_payment": meta_payment["is_general_payment"],
                "direct_payment": meta_payment["direct_payment"]
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


