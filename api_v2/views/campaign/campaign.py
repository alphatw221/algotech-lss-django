import json

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign, CampaignSerializer, CampaignSerializerEdit, CampaignSerializerRetreive, CampaignSerializerCreate
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
from api.models.youtube.youtube_channel import YoutubeChannelSerializer
from backend.api.google.user import api_google_post_refresh_token

from backend.pymongo.mongodb import db
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import getdata,getparams
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from bson.json_util import loads, dumps
from api.utils.rule.rule_checker.user_subscription_rule_checker import CreateCampaignRuleChecker

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

class CampaignPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all().order_by('id')
    serializer_class = CampaignSerializer
    filterset_fields = []
    pagination_class = CampaignPagination

    @action(detail=False, methods=['GET'], url_path=r'list_campaign', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_campaign(self, request):
        api_user, keyword, campaign_status, order_by, search_column = getparams(request,("keyword", "status", "order_by","searchColumn"), with_user=True, seller=True)
        
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaigns = user_subscription.campaigns.filter(id__isnull=False) # Due to problematic dirty data
        if campaign_status == 'history':
            campaigns = campaigns.filter(end_at__lt=datetime.utcnow())
        elif campaign_status == 'schedule':
            campaigns = campaigns.filter(end_at__gte=datetime.utcnow())
        elif campaign_status == 'ongoing':
            campaigns = campaigns.filter(end_at__gte=datetime.utcnow())
            campaigns = campaigns.filter(start_at__lte=datetime.utcnow())
        if order_by:
            campaigns = campaigns.order_by("-"+order_by)
        
        kwargs = {}
        if (search_column in ["", None]) and (keyword not in [None, ""]):
            raise ApiVerifyError("search_column field can not be empty when keyword has value")
        if (search_column not in ['undefined', '']) and (keyword not in ['undefined', '', None]):
            kwargs = { search_column + '__icontains': keyword }

        campaigns = campaigns.filter(**kwargs)
        page = self.paginate_queryset(campaigns)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(campaigns, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)