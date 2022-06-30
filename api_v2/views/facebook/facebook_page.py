from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from api import models
import lib

class FacebookPageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.facebook.facebook_page.FacebookPage.objects.all().order_by('id')
    serializer_class = models.facebook.facebook_page.FacebookPageSerializer
    filterset_fields = []

    
    @action(detail=True, methods=['GET'], url_path=r'token/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_facebook_page_token(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'facebook' not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiVerifyError('facebook not activated')
        
        facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, pk)
        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('facebook', facebook_page.token, facebook_page.page_id)
        if not is_token_valid:
            raise lib.error_handle.error.api_error.ApiVerifyError(f"Facebook page <{facebook_page.name}>: token expired or invalid. Please re-bind your page on Platform page.")
        return Response(models.facebook.facebook_page.FacebookPageSerializer(facebook_page).data, status=status.HTTP_200_OK)