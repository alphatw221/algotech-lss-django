from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes

from api import models
from api.utils.common.order_helper import PreOrderHelper
from api.utils.advance_query.dashboard import get_campaign_merge_order_list_v2
from bson.json_util import loads, dumps
import lib   
    
    
class DashboardViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.order.order.Order.objects.all().order_by('id')
    filterset_fields = []
    
    @action(detail=False, methods=['POST'], url_path=r'order_list')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_merge_order_list(self, request):

        api_user, campaign_id, search, page, page_size= lib.util.getter.getparams(request, ( 'campaign_id', 'search', 'page', 'page_size'),with_user=True, seller=True)
        f_payment,f_delivery,f_platform = lib.util.getter.getdata(request,('payment','delivery','platform'))
        
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)
        merge_list = get_campaign_merge_order_list_v2(campaign.id, search,f_payment,f_delivery,f_platform)
        
        page,page_size = int(page),int(page_size)
        skip = (page-1)*page_size
        if len(merge_list) >= page_size:
            merge_list = merge_list[skip:skip+page_size]
        merge_list_str = dumps(merge_list)
        merge_list_json = loads(merge_list_str)

        return Response({'count':len(merge_list),'data':merge_list_json}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'edit_allow_checkout')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def campaign_edit_allow_checkout(self, request):

        api_user, campaign_id, _status= lib.util.getter.getparams(request, ('campaign_id', 'status'))

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)

        campaign.meta['allow_checkout']=1 if int(_status) else 0
        campaign.save()

        return Response({"allow_checkout":campaign.meta['allow_checkout']
                         }, status=status.HTTP_200_OK)