from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User, UserSerializer
from api.views.user._user import seller_login_helper, customer_login_helper
from backend.api.facebook.user import api_fb_get_accounts_from_user
from backend.api.facebook.page import api_fb_get_page_picture
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage
from datetime import datetime


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = []

    @action(detail=False, methods=['POST'], url_path=r'customer_login')
    def customer_login(self, request, pk=None):

        return customer_login_helper(self, request, pk=None)

    @action(detail=False, methods=['POST'], url_path=r'user_login')
    def user_login(self, request, pk=None):
        return seller_login_helper(self, request, pk=None)

    @action(detail=False, methods=['GET'], url_path=r'facebook_pages')
    def get_facebook_pages_by_client(self, request):

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        status_code, response = api_fb_get_accounts_from_user(
            user_token=api_user.facebook_info['token'], user_id=api_user.facebook_info['id'])

        if status_code != 200:
            return Response({'message': 'api_fb_get_accounts_from_user error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        for item in response['data']:
            page_token = item['access_token']
            page_id = item['id']
            page_name = item['name']
            status_code, picture_data = api_fb_get_page_picture(
                page_token=page_token, page_id=page_id, height=100, width=100)
            item['image'] = picture_data['data']['url'] if status_code == 200 else None
            if FacebookPage.objects.filter(page_id=page_id).exists():
                FacebookPage.objects.filter(page_id=page_id).update(token=page_token, token_update_at=datetime.now(
                ), token_update_by=api_user.facebook_info['id'], image=item['image'])
            else:
                FacebookPage.objects.create(
                    page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=item['image'])

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'facebook_pages')
    def get_facebook_pages_by_server(self, request, pk=None):

        if not User.objects.filter(id=pk).exists():
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)

        api_user = User.objects.get(id=pk)
        if api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        status_code, response = api_fb_get_accounts_from_user(
            user_token=api_user.facebook_info['token'], user_id=api_user.facebook_info['id'])

        if status_code != 200:
            return Response({'message': 'api_fb_get_accounts_from_user error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        for item in response['data']:
            page_token = item['access_token']
            page_id = item['id']
            page_name = item['name']
            status_code, picture_data = api_fb_get_page_picture(
                page_token=page_token, page_id=page_id, height=100, width=100)
            item['image'] = picture_data['data']['url'] if status_code == 200 else None
            if FacebookPage.objects.filter(page_id=page_id).exists():
                FacebookPage.objects.filter(page_id=page_id).update(token=page_token, token_update_at=datetime.now(
                ), token_update_by=api_user.facebook_info['id'], image=item['image'])
            else:
                FacebookPage.objects.create(
                    page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=item['image'])

        return Response(response, status=status.HTTP_200_OK)
