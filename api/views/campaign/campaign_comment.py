from email import message
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import getdata,getparams
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

from api.models.campaign.campaign_comment import CampaignComment, CampaignCommentSerializer, CampaignCommentSerializerTest
from api import models

import lib
from django.core import serializers
from bson.json_util import loads, dumps

from service.instagram.post import get_post_media_url

class CampaignCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignComment.objects.all().order_by('id')
    serializer_class = CampaignCommentSerializer
    filterset_fields = []

    @action(detail=False, methods=['GET'], url_path=r'summerize/<campaign_id>[^/.]+', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_summerize_comment_main_categories(self, request, campaign_id):

        since, count = lib.util.getter.getparams(
            request, ('since', 'count',), with_user=False)
        
        if not since:
            since =1 

        if not count:
            count = 20

        comments = models.campaign.campaign_comment.CampaignComment.objects.filter(campaign=campaign_id).all()
        
        main_categories = serializers.serialize("json", comments.all(), fields=("id","categories", "message", "main_categories"))
        res = loads(main_categories)

        main_categories = CampaignCommentSerializerTest(comments.all(),many=True)
        print(main_categories)
        res = main_categories.data

        return Response(res, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_comment(self, request, campaign_id):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        # comments = models.campaign.campaign_comment.CampaignComment.objects.filter(campaign=campaign_id)
        # fb_comments = comments.filter(platform='facebook').order_by('-created_time')
        # ig_comments = comments.filter(platform='instagram').order_by('-created_time')
        # yt_comments = comments.filter(platform='youtube').order_by('-created_time')
        ig_media_url = None
        try:
            status_code, response = get_post_media_url(campaign.instagram_profile.token, campaign.instagram_campaign.get("live_media_id", ""))
            if status_code == 200:
                ig_media_url = response["media_url"]
        except Exception as e:
            print(e)
        res = {
            "all": {
                "fully_setup": True
            },
            "facebook": {
                # "comments":CampaignCommentSerializer(fb_comments, many=True).data,
                "fully_setup": True if (campaign.facebook_campaign.get("post_id", None) and campaign.facebook_page) else False,
                "page_id": campaign.facebook_page.page_id,
                "post_id": campaign.facebook_campaign.get("post_id", None),
            },
            "instagram": {
                # "comments":CampaignCommentSerializer(ig_comments, many=True).data,
                "fully_setup": True if (campaign.instagram_campaign.get("live_media_id", None) and campaign.instagram_profile) else False,
                "media_url": ig_media_url
            },
            "youtube": {
                # "comments":CampaignCommentSerializer(yt_comments, many=True).data,
                "fully_setup": True if (campaign.youtube_campaign.get("live_video_id", None) and campaign.youtube_channel) else False,
                "live_video_id": campaign.youtube_campaign.get("live_video_id", None)
            },
            
        }
        return Response(res, status=status.HTTP_200_OK)    



