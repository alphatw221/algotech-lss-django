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
    def check_youtube_channel_token(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'youtube' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('youtube_not_activated')
        
        youtube_channel = lib.util.verify.Verify.get_youtube_channel_from_user_subscription(user_subscription, pk)
        refresh_api_status, refresh_response = service.google.user.api_google_post_refresh_token(youtube_channel.refresh_token)
        if refresh_api_status == 200:
            youtube_channel.token = refresh_response.get('access_token')
            youtube_channel.save()

        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('youtube', youtube_channel.token, youtube_channel.channel_id)
        if not is_token_valid:
            raise lib.error_handle.error.api_error.ApiVerifyError("youtube_token_expired")
        return Response(models.youtube.youtube_channel.YoutubeChannelSerializer(youtube_channel).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'post/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_youtube_channel_post(self, request, pk):
        live_video_id = request.query_params.get('post_id')
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'youtube' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('youtube_not_activated')
        
        youtube_channel = lib.util.verify.Verify.get_youtube_channel_from_user_subscription(user_subscription, pk)
        
        refresh_api_status, refresh_response = service.google.user.api_google_post_refresh_token(youtube_channel.refresh_token)
        if refresh_api_status == 200:
            youtube_channel.token = refresh_response.get('access_token')
            youtube_channel.save()
            
        code, response = service.youtube.viedo.get_video_info_with_access_token(youtube_channel.token, live_video_id)
        if not response.get('items'):
            return Response({"error_response": response}, status=status.HTTP_200_OK)
        return Response({"success_response": response}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'live_broadcasts', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_youtube_channel_live_broadcasts(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'youtube' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('youtube_not_activated')
        
        youtube_channel = lib.util.verify.Verify.get_youtube_channel_from_user_subscription(user_subscription, pk)
        
        refresh_api_status, refresh_response = service.google.user.api_google_post_refresh_token(youtube_channel.refresh_token)
        if refresh_api_status == 200:
            youtube_channel.token = refresh_response.get('access_token')
            youtube_channel.save()
            
        code, response = service.youtube.channel.get_live_broadcasts(youtube_channel.token)
        print(response)
        if code !=200:
            return Response({"error_response": response}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_200_OK)
