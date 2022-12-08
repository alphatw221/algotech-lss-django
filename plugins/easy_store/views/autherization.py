from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth.models import User as AuthUser

from api import models
import lib
import service

from .. import service as easy_store_service

from automation import jobs

PLUGIN_EASY_STORE = 'easy_store'
EASY_STORE_APP_CLIENT_ID= "appc776480369afe45e"
EASY_STORE_APP_CLIENT_SECRET= "1f2c16866c7fd4930a183bdcb6476a76"

class AuthorizationViewSet(viewsets.GenericViewSet):
    queryset = models.user.user.User.objects.none()

    @action(detail=False, methods=['POST'], url_path=r'credential/exchange', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def exchange_easy_store_credential(self, request):
        print(request.data)
        code, shop, email, password = lib.util.getter.getdata(request, ("code", "shop", "email","password",), required=True)

        if not AuthUser.objects.filter(email=email).exists():
            return

        auth_user = AuthUser.objects.get(email=email)

        if not auth_user.check_password(password):
            raise lib.error_handle.error.api_error.ApiVerifyError('email_or_password_incorrect')

        if not auth_user.api_users.filter(type='user').exists():
            raise lib.error_handle.error.api_error.ApiVerifyError('util.no_api_user_found')
        api_user = auth_user.api_users.get(type='user')


        if auth_user.api_users.filter(type='user').exists():
            lib.util.marking_tool.NewUserMark.check_mark(auth_user.api_users.get(type='user'), save=True)

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        success, data = easy_store_service.autherization.exchange_token(shop, code, EASY_STORE_APP_CLIENT_ID, EASY_STORE_APP_CLIENT_SECRET)
        if not success:
            raise lib.error_handle.error.api_error.ApiCallerError('authorization fail, please contact support team')

        credential = {'shop':shop, 'access_token':data.get('access_token')}
        if user_subscription.user_plan.get('plugins'):
            user_subscription.user_plan['plugins']['easy_store']=credential
        else:
            user_subscription.user_plan['plugins']={'easy_store':credential}

        user_subscription.save()

        return Response('ok', status=status.HTTP_200_OK)
