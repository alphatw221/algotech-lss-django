from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from api import models
from api.models.instagram import instagram_profile
import lib

import service

class YoutubeChannelViewSet(viewsets.GenericViewSet):
    queryset = models.youtube.youtube_channel.YoutubeChannel.objects.all()

    @action(detail=True, methods=['GET'], url_path=r'token/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_instagram_page_token(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'youtube' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('youtube not activated')
        
        youtube_channel = lib.util.verify.Verify.get_youtube_channel_from_user_subscription(user_subscription, pk)
        service.google.user.api_google_post_refresh_token(youtube_channel.refresh_token)
        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('youtube', youtube_channel.token, youtube_channel.channel_id)
        if not is_token_valid:
            raise lib.error_handle.error.api_error.ApiVerifyError(f"YouTube channel <{youtube_channel.name}>: token expired or invalid. Please re-bind your channel on Platform page.")
        return Response(models.youtube.youtube_channel.YoutubeChannelSerializer(youtube_channel).data, status=status.HTTP_200_OK)

