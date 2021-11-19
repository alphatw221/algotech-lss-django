from datetime import datetime
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User, UserSerializer
from api.views.user._user import login_helper

from api.models.facebook.facebook_page import FacebookPage
from rest_framework.response import Response
from rest_framework import status

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = []

    @action(detail=False, methods=['POST'], url_path=r'customer_login')
    def customer_login(self, request, pk=None):

        return login_helper(self, request, 'customer', pk=None)

    @action(detail=False, methods=['POST'], url_path=r'user_login')
    def user_login(self, request, pk=None):
        return login_helper(self, request, 'user', pk=None)

    @action(detail=False, methods=['POST'], url_path=r'bind_facebook_page')
    def bind_facebook_page(self, request, pk=None):

        items = request.data.get('data')
        api_user = request.user.api_users.get(type='user')
        api_user.facebook_info['pages'] = {}
        for item in items:
            page_token = item['access_token']
            page_id = item['id']
            page_name = item['name']

            if FacebookPage.objects.filter(page_id=page_id).exists():
                FacebookPage.objects.filter(page_id=page_id).update(token=page_token, token_update_at=datetime.now(
                ), token_update_by=api_user.facebook_info['id'])
            else:
                FacebookPage.objects.create(
                    page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'])

            api_user.facebook_info['pages'][page_id] = item

        api_user.save()

        return Response('complete', status=status.HTTP_200_OK)
