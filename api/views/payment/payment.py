from rest_framework import views, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings

from django.core.files.storage import default_storage

from api.utils.common.common import api_error_handler, getparams, ApiVerifyError

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
        elif api_user.status != "valid":
            raise ApiVerifyError("not activated user")

        _, _, pre_order = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)