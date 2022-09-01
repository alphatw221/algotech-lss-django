
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

class TwitchViewSet(viewsets.GenericViewSet):
    queryset = models.twitch.twitch_channel.TwitchChannel.objects.all()

    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/bulk/create/comment', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def capture_twitch_comment(self, request, campaign_id):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        if 'twitch' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('twitch not activated')
        
        service.rq.queue.enqueue_campaign_queue(jobs.comment_create_job.comment_create_job, campaign_id = campaign.id, comments = request.data, platform='twitch', push_comment = True)

        return Response({'message': 'enqueue success'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'token/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_twitch_channel_token(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'twitch' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('twitch_not_activated')
        
        twitch_channel = lib.util.verify.Verify.get_twitch_channel_from_user_subscription(user_subscription, pk)
        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('twitch', twitch_channel.token)
        if not is_token_valid:
            status_code, response = service.twitch.twitch.refresh_exchange_access_token(twitch_channel.refresh_token)
            if status_code / 100 == 2:
                twitch_channel.token = response['access_token']
                twitch_channel.refresh_token = response['refresh_token']
                twitch_channel.save()
            else:
                raise lib.error_handle.error.api_error.ApiVerifyError("twitch_token_expired")
        return Response(models.twitch.twitch_channel.TwitchChannelInfoSerializer(twitch_channel).data, status=status.HTTP_200_OK)
