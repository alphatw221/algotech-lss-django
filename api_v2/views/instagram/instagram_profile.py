from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from api import models
from api.models.instagram import instagram_profile
import lib
import service


class InstagramProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.instagram.instagram_profile.InstagramProfile.objects.all().order_by('id')
    serializer_class =  models.instagram.instagram_profile.InstagramProfileSerializer
    filterset_fields = []


    @action(detail=True, methods=['GET'], url_path=r'token/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_instagram_profile_token(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'instagram' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('instagram_not_activated')
        
        instagram_profile = lib.util.verify.Verify.get_instagram_profile_from_user_subscription(user_subscription, pk)
        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('instagram', instagram_profile.token, instagram_profile.business_id)
        if not is_token_valid:
            raise lib.error_handle.error.api_error.ApiVerifyError("instagram_token_expired")
        return Response(models.instagram.instagram_profile.InstagramProfileSerializer(instagram_profile).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'post/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_instagram_profile_post(self, request, pk):
        media_id = request.query_params.get('post_id')
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'instagram' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('instagram_not_activated')
        
        instagram_profile = lib.util.verify.Verify.get_instagram_profile_from_user_subscription(user_subscription, pk)
        code, response = service.instagram.post.get_post(instagram_profile.token, media_id)
        if code !=200:
            return Response({"error_response": response}, status=status.HTTP_200_OK)
        return Response({"success_response": response}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'picture', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_instagram_profile_picture(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        instagram_profile = models.instagram.instagram_profile.InstagramProfile.objects.get(id=pk)
        code, response = service.instagram.profile.get_profile_info(page_token=instagram_profile.token, profile_id=instagram_profile.business_id)
        if code !=200:
            return Response({"error_response": response}, status=status.HTTP_400_BAD_REQUEST)
        instagram_profile.image = response['profile_picture_url']
        instagram_profile.save()
        return Response(instagram_profile.image, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'live_media', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_instagram_profile_live_media(self, request, pk):
        limit = request.query_params.get('limit')
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        instagram_profile = models.instagram.instagram_profile.InstagramProfile.objects.get(id=pk)
        code, response = service.instagram.profile.get_profile_live_media(page_token=instagram_profile.token, profile_id=instagram_profile.business_id, limit=limit)
        if code !=200:
            return Response({"error_response": response}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'media', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_instagram_profile_media(self, request, pk):
        limit = request.query_params.get('limit')
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        instagram_profile = models.instagram.instagram_profile.InstagramProfile.objects.get(id=pk)
        code, response = service.instagram.profile.get_profile_media(page_token=instagram_profile.token, profile_id=instagram_profile.business_id, limit=limit)
        if code !=200:
            return Response({"error_response": response}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_200_OK)

