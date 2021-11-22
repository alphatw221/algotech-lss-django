from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User, UserSerializer
from api.views.user._user import seller_login_helper, customer_login_helper


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = []

    @action(detail=False, methods=['POST'], url_path=r'customer_login')
    def customer_login(self, request, pk=None):

        return customer_login_helper(self, request, pk=None)

    @action(detail=False, methods=['POST'], url_path=r'user_login')
    def user_login(self, request, pk=None):
        return seller_login_helper(self, request, pk=None)

    @action(detail=False, methods=['GET'], url_path=r'user_facebook_pages')
    def user_facebook_pages(self, request, pk=None):

        request.user
        # TODO 驗證身分

        # TODO 後續改成模組

        return seller_login_helper(self, request, pk=None)
