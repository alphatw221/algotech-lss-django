
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from api import models
import service
import lib




class UserViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = models.user.user.User.objects.all().order_by('id')
    serializer_class = models.user.user.UserSerializer
    filterset_fields = []

#-----------------------------------------admin----------------------------------------------------------------------------------------------



#-----------------------------------------buyer----------------------------------------------------------------------------------------------

    @action(detail=False, methods=['POST'], url_path=r'buyer/login/facebook', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_login_with_facebook(self, request):
        token = lib.helper.login_helper.FacebookLogin.get_token(request.data.get('facebook_token'),user_type='customer')
        return Response(token, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'buyer/login/google', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_login_with_google(self, request):

        token = lib.helper.login_helper.GoogleLogin.get_token(token=request.data.get('google_token'),user_type='customer')
        return Response(token, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer/account', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_get_account_info(self, request):
        api_user = lib.util.verify.Verify.get_customer_user(request)
        return Response(models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK)    

#-----------------------------------------seller----------------------------------------------------------------------------------------------
    
    @action(detail=False, methods=['POST'], url_path=r'seller/login/facebook', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_login_with_facebook(self, request):
        token = lib.helper.login_helper.FacebookLogin.get_token(request.data.get('facebook_token'),user_type='user')
        return Response(token, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'seller/login/google', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_login_with_google(self, request):

        token = lib.helper.login_helper.GoogleLogin.get_token(token=request.data.get('google_token'),user_type='user')
        return Response(token, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller/account', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_get_account_info(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        return Response(models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK) 

