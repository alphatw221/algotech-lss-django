from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from api import models
import lib
import service

class FacebookPageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.facebook.facebook_page.FacebookPage.objects.all().order_by('id')
    serializer_class = models.facebook.facebook_page.FacebookPageSerializer
    filterset_fields = []

    
    @action(detail=True, methods=['GET'], url_path=r'token/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_facebook_page_token(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'facebook' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('facebook_not_activated')
        
        facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, pk)
        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('facebook', facebook_page.token, facebook_page.page_id)
        if not is_token_valid:
            raise lib.error_handle.error.api_error.ApiVerifyError("facebook_token_expired")
        return Response(models.facebook.facebook_page.FacebookPageSerializer(facebook_page).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'post/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_facebook_page_post(self, request, pk):
        post_id = request.query_params.get('post_id')
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'facebook' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('facebook_not_activated')
        
        facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, pk)
        code, response = service.facebook.post.get_post_comments(facebook_page.token, post_id)
        if code !=200:
            return Response({"error_response": response}, status=status.HTTP_200_OK)
        return Response({"success_response": response}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path=r'create/live_object', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_live_object(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, pk)
        code, response = service.facebook.post.post_get_live_video_object(facebook_page.token, facebook_page.page_id)
        if code !=200:
            return Response({"error_response": response}, status=status.HTTP_200_OK)
        return Response(response, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'picture', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_profile_picture(self, request, pk):
        try:
            api_user = lib.util.verify.Verify.get_seller_user(request)
            user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
            facebook_page = models.facebook.facebook_page.FacebookPage.objects.get(id=pk)
            code, response = service.facebook.page.get_page_picture(page_token=facebook_page.token, page_id=facebook_page.page_id, height=600, width=600)
            if code !=200:
                return Response({"error_response": response}, status=status.HTTP_200_OK)
            facebook_page.image = response['data']['url']
            facebook_page.save()
            return Response(facebook_page.image, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error_response": str(e)}, status=status.HTTP_200_OK)