from rest_framework import views, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings

from django.core.files.storage import default_storage

from api.utils.common.common import api_error_handler, getparams, ApiVerifyError
from api.models.order.order import Order
from api.models.user.user_subscription import UserSubscription
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile

import datetime
import hashlib

platform_dict = {'facebook':FacebookPage, 'youtube':YoutubeChannel, 'instagram':InstagramProfile}

class PaymentViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    permission_classes = [IsAdminUser | IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def test(self, request, *args, **kwargs):
        return Response({'msg': 'TestViewSet test accomplished.'})


    @action(detail=False, methods=['GET'], url_path=r'get_ipg_order_data')
    @api_error_handler
    def get_ipg_order_data(self, request, pk=None):
        api_user, order_id = getparams(
            request, ("order_id", ), seller=False)

        if not api_user:
            raise ApiVerifyError("no user found")

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

        ipg = user_subscription.meta_payment['ipg']

        storename = ipg['store_name']
        txndatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chargetotal = order.total
        shared_secret = ipg['shared_secret']
        payment_hash=hashlib.sha256((storename + str(txndatetime) + str(chargetotal) + shared_secret).encode('utf-8')).hexdigest()
        currency = ipg['currency']

        data={
            "storename":ipg['storename'],
            "txntype":"sale",
            "mode":"payonly",
            "timezone":"Asia/Singapore", #TODO
            "txndatetime": txndatetime,
            "hash_algorithm":"SHA256",
            "hash":payment_hash,
            "chargetotal":chargetotal,
            "currency":currency,
            "responseSuccessURL":"",
            "responseFailURL":""
        }


        return Response(data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['GET'], url_path=r'ipg_payment_success')
    # @api_error_handler
    # def get_ipg_order_data(self, request, pk=None):
        
    #     api_user, order_id = getparams(
    #         request, ("order_id", ), seller=False)


    #     # OrderMetaModel::api_update($order_id, 'payment_info', $request->post('ipgTransactionId'));
    #     # OrderMetaModel::api_update($order_id, 'payment_info_ccbrand', $request->post('ccbrand'));
    #     # OrderMetaModel::api_update($order_id, 'payment_info_cardnumber', $request->post('cardnumber'));
    #     # OrderMetaModel::api_update($order_id, 'payment_method', 'First Data IPG');

    #     # (new OrderController)->checkout_process($campaign_id, $fb_psid, $order_id);
    #     # (new EmailController)->send_order($order_id);
    #     # return redirect()->route('page_confirmation', ['campaign_id' => $campaign_id, 'order_id' => $order_id]);


    #     return Response(data, status=status.HTTP_200_OK)
