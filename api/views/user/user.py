from datetime import datetime
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User, UserSerializer
from api.views.user._user import login_helper

from api.models.facebook.facebook_page import FacebookPage


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

    # @action(detail=False, methods=['POST'], url_path=r'bind_facebook_page')
    # def bind_facebook_page(self, request, pk=None):

    #     api_user = request.user.api_users.get(type='user')

    #     facebook_info = api_user.facebook_info
    #     items = request.data.get('data')

    #     pages = {}
    #     for item in items:
    #         page_token = item['access_token']
    #         page_id = item['id']
    #         page_name = item['name']

    #         if FacebookPage.objects.filter(page_id=page_id).exists():
    #             facebook_page = FacebookPage.objects.create(
    #                 page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=str(api_user.id))
    #         else:
    #             facebook_page = FacebookPage.objects.get(page_id=page_id)
    #             facebook_page.update(token=page_token, token_update_at=datetime.now(
    #             ), token_update_by=str(api_user.id))

    #         pages[page_id]=item

    #     return Response(ret, status=status.HTTP_200_OK)
