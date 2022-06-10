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
from api.models.facebook.facebook_page import FacebookPageSerializer
from api.models.instagram.instagram_profile import InstagramProfileSerializer
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

    @action(detail=False, methods=['GET'], url_path=r'list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_campaign(self, request):
        api_user, keyword, campaign_status, order_by, search_column = getparams(request,("keyword", "status", "order_by","searchColumn"), with_user=True, seller=True)
        
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaigns = user_subscription.campaigns.filter(id__isnull=False) # Due to problematic dirty data
        if campaign_status == 'history':
            campaigns = campaigns.filter(end_at__lt=datetime.utcnow())
        elif campaign_status == 'scheduled':
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
    
    @action(detail=False, methods=['GET'], url_path=r'check_facebook_page_token', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def check_facebook_page_token(self, request):

        api_user, facebook_page_id = getparams(request, ('facebook_page_id',),with_user=True, seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        if 'facebook' not in user_subscription.user_plan.get('activated_platform'):
           raise ApiVerifyError('facebook not activated')
       
        facebook_page = Verify.get_facebook_page_from_user_subscription(user_subscription, facebook_page_id)
        is_token_valid = Verify.check_is_page_token_valid('facebook', facebook_page.token, facebook_page.page_id)
        if not is_token_valid:
            raise ApiVerifyError(f"Facebook page <{facebook_page.name}>: token expired or invalid. Please re-bind your page on Platform page.")
        return Response(FacebookPageSerializer(facebook_page).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'check_youtube_channel_token', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def check_youtube_channel_token(self, request):

        api_user, youtube_channel_id = getparams(request, ('youtube_channel_id',),with_user=True, seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        if 'youtube' not in user_subscription.user_plan.get('activated_platform'):
           raise ApiVerifyError('youtube not activated')

        youtube_channel = Verify.get_youtube_channel_from_user_subscription(user_subscription, youtube_channel_id)
        print(youtube_channel)
        response_status, response = api_google_post_refresh_token(youtube_channel.refresh_token)
        print(response)
        is_token_valid = Verify.check_is_page_token_valid('youtube', response['access_token'])
        if not is_token_valid:
            raise ApiVerifyError(f"YouTube channel <{youtube_channel.name}>: token expired or invalid. Please re-bind your channel on Platform page.")
        youtube_channel.token = response['access_token']
        youtube_channel.save()
        return Response(YoutubeChannelSerializer(youtube_channel).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'check_instagram_profile_token', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def check_instagram_profile_token(self, request):

        api_user, instagram_profile_id = getparams(request, ('instagram_profile_id',),with_user=True, seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        if 'instagram' not in user_subscription.user_plan.get('activated_platform'):
           raise ApiVerifyError('instagram not activated')

        instagram_profile = Verify.get_instagram_profile_from_user_subscription(user_subscription, instagram_profile_id)
        is_token_valid = Verify.check_is_page_token_valid('instagram', instagram_profile.token, instagram_profile.business_id)
        if not is_token_valid:
            raise ApiVerifyError(f"Instagram profile <{instagram_profile.name}>: token expired or invalid. Please re-bind your profile on Platform page.")
        return Response(InstagramProfileSerializer(instagram_profile).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'], url_path=r'save_pages_info', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def save_pages_info(self, request, pk):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription, pk)
        
        data = request.data
        print(data)
        if post_id := data.get("facebook", {}).get("post_id", {}):
            facebook_page = Verify.get_facebook_page_from_user_subscription(user_subscription, data.get("facebook", {}).get("page_id", {}), field="page_id")
            campaign.facebook_page = facebook_page
            campaign.facebook_campaign['post_id'] = post_id
        if live_video_id := data.get("youtube", {}).get("live_video_id", {}):
            youtube_channel = Verify.get_youtube_channel_from_user_subscription(user_subscription, data.get("youtube", {}).get("channel_id", {}), field="channel_id")
            campaign.youtube_channel = youtube_channel
            campaign.youtube_campaign['live_video_id'] = live_video_id
        if live_media_id := data.get("instagram", {}).get("live_media_id", {}):
            instagram_profile = Verify.get_instagram_profile_from_user_subscription(user_subscription, data.get("instagram", {}).get("profile_id", {}), field="business_id")
            campaign.instagram_profile = instagram_profile
            campaign.instagram_campaign['live_media_id'] = live_media_id
        campaign.save()
        
        return Response("ok", status=status.HTTP_200_OK)

