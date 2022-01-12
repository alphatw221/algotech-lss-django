from rest_framework import views, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings

from django.core.files.storage import default_storage

from api.utils.common.common import api_error_handler, getdata, getparams, ApiVerifyError
from api.models.order.order import Order
from api.models.user.user_subscription import UserSubscription
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile

import datetime
import hashlib
from django.http import HttpResponseRedirect

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
        
        api_user, order_id = getparams(
            request, ("order_id", ), seller=False)

        approval_code, oid, refnumber, trancaction_status, approval_code, txndate_processed, ipgTransactionId, fail_reason, response_hash = getdata(request, ("approval_code", "oid", "refnumber", "status", "approval_code", "txndate_processed", "ipgTransactionId", "fail_reason", "response_hash"))
        
        
        
        
        # OrderMetaModel::api_update($order_id, 'payment_info', $request->post('ipgTransactionId'));
        # OrderMetaModel::api_update($order_id, 'payment_info_ccbrand', $request->post('ccbrand'));
        # OrderMetaModel::api_update($order_id, 'payment_info_cardnumber', $request->post('cardnumber'));
        # OrderMetaModel::api_update($order_id, 'payment_method', 'First Data IPG');

        # (new OrderController)->checkout_process($campaign_id, $fb_psid, $order_id);
        # (new EmailController)->send_order($order_id);
        # return redirect()->route('page_confirmation', ['campaign_id' => $campaign_id, 'order_id' => $order_id]);


        return Response(data, status=status.HTTP_200_OK)

