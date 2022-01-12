from rest_framework import views, viewsets, status
import paypalrestsdk
from django.http import HttpResponseRedirect
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser

from api.utils.common.common import api_error_handler, getdata, getparams, ApiVerifyError
from api.models.order.order import Order
from api.models.user.user_subscription import UserSubscription
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile

import datetime
import hashlib
from django.http import HttpResponseRedirect
from api.views.payment._payment import HitPay_Helper
from backend.pymongo.mongodb import db

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
