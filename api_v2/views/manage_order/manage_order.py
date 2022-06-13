from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes

from api import models
from api.utils.common.order_helper import PreOrderHelper
from api.utils.advance_query.dashboard import get_campaign_merge_order_list
from bson.json_util import loads, dumps
import lib   
    
    
class DashboardViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.order.order.Order.objects.all().order_by('id')
    filterset_fields = []
    
    @action(detail=False, methods=['GET'], url_path=r'order_list')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_merge_order_list(self, request):

        api_user, campaign_id, search, page, page_size=getparams(request, ( 'campaign_id', 'search', 'page', 'page_size'),with_user=True, seller=True)

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)
        merge_list = get_campaign_merge_order_list(campaign.id, search, page, page_size)

        merge_list_str = dumps(merge_list)
        merge_list_json = loads(merge_list_str)

        return Response(merge_list_json, status=status.HTTP_200_OK)