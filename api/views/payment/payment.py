from rest_framework import views, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import default_storage

from api.utils.common.common import api_error_handler, getparams, ApiVerifyError
from api.views.payment._payment import HitPay_Helper
from backend.pymongo.mongodb import db


class PaymentViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    permission_classes = [IsAdminUser | IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def test(self, request, *args, **kwargs):
        return Response({'msg': 'TestViewSet test accomplished.'})


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

    @action(detail=False, methods=['GET'], url_path=r'hit_pay')
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
    
    @action(detail=False, methods=['POST'], url_path=r'hit_pay_webhook')
    def hit_pay_webhook(self, request):
        api_user, payment_id, payment_request_id, phone, amount, currency, status, reference_number, hmac = getparams(
            request, ("payment_id", "payment_request_id", "phone", "amount", "currency", "status", "reference_number", "hmac"))
        hitpay_dict, info_dict = {}, {}
        secret_salt = '2MUizyJj429NIoOMmTXedyICmbwS1rt6Wph7cGqzG99IkmCV6nUCQ22lRVCB0Rgu'

        info_dict['payment_id'] = payment_id
        info_dict['payment_request_id'] = payment_request_id
        hitpay_dict['hitpay'] = info_dict
        total = int(db.api_order.find_one({'id': int(reference_number)})['total'])

        if status == 'completed' and total == int(amount) and hmac == secret_salt:
            db.api_order.update_one(
                { 'id': int(reference_number) },
                { '$set': {'status': 'paid', 'checkout_details': hitpay_dict} }
            )

        return Response('request')