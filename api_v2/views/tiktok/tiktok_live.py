
from platform import platform
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from automation import jobs
from api import models
import lib
import database
import service

from datetime import datetime

class TikTokViewSet(viewsets.GenericViewSet):
    queryset = models.twitch.twitch_channel.TwitchChannel.objects.none()

    @action(detail=False, methods=['POST'], url_path=r'comment/process/(?P<campaign_id>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def process_tiktok_live_comments(self, request, campaign_id):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)


        if 'tiktok' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('tiktok_not_activated')
        
        service.rq.queue.enqueue_test_queue(jobs.comment_create_job.comment_create_job, campaign_id = campaign.id, comments = request.data, platform='tiktok', push_comment = True)
        # service.rq.queue.enqueue_campaign_queue(jobs.comment_create_job.comment_create_job, campaign_id = campaign.id, comments = request.data, platform='tiktok', push_comment = True)
        return Response({'message': 'enqueue success'}, status=status.HTTP_200_OK)
