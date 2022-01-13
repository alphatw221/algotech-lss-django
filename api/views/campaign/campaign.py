from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign, CampaignSerializer, CampaignSerializerRetreive, CampaignSerializerCreate
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime

from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import *
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

def verify_request(api_user, platform_name, platform_id, campaign_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)

    if campaign_id:
        if not platform.campaigns.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = platform.campaigns.get(id=campaign_id)
        return platform, campaign

    return platform


class CampaignPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CampaignViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Campaign.objects.all().order_by('id')
    serializer_class = CampaignSerializer
    filterset_fields = []
    pagination_class = CampaignPagination

    @action(detail=True, methods=['GET'], url_path=r'retrieve_campaign')
    @api_error_handler
    def retrieve_campaign(self, request, pk=None):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        api_user = request.user.api_users.get(type='user')

        _, campaign = verify_request(
            api_user, platform_name, platform_id, campaign_id=pk)
        serializer = CampaignSerializerRetreive(campaign)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_campaign')
    @api_error_handler
    def list_campaign(self, request):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        order_by = request.query_params.get('order_by')
        campaign_status = request.query_params.get('status')
        key_word = request.query_params.get('key_word')
        api_user = request.user.api_users.get(type='user')

        platform = verify_request(api_user, platform_name, platform_id)

        campaigns = platform.campaigns.all()
        if campaign_status == 'history':
            campaigns = campaigns.filter(end_at__lt=datetime.now())
        elif campaign_status == 'schedule':
            campaigns = campaigns.filter(end_at__gte=datetime.now())
        if key_word:
            campaigns = campaigns.filter(title__icontains=str(key_word))
        if order_by:
            campaigns = campaigns.order_by(order_by)

        page = self.paginate_queryset(campaigns)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(campaigns, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_campaign')
    @api_error_handler
    def create_campaign(self, request):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        api_user = request.user.api_users.get(type='user')

        platform = verify_request(api_user, platform_name, platform_id)

        print(platform)
        data = request.data
        data['created_by'] = api_user.id
        # TODO 之後要改寫
        data['facebook_page'] = platform.id if platform_name == 'facebook' else None
        data['youtube_channel'] = platform.id if platform_name == 'youtube' else None
        data['instagram_profile'] = platform.id if platform_name == 'instagram' else None
        serializer = CampaignSerializerCreate(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_campaign')
    @api_error_handler
    def update_campaign(self, request, pk=None):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        api_user = request.user.api_users.get(type='user')

        _, campaign = verify_request(
            api_user, platform_name, platform_id, campaign_id=pk)

        serializer = self.get_serializer(
            campaign, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_campaign')
    @api_error_handler
    def delete_campaign(self, request, pk=None):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        api_user = request.user.api_users.get(type='user')

        _, campaign = verify_request(
            api_user, platform_name, platform_id, campaign_id=pk)
        campaign.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
