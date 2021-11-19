from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User, UserSerializer
from api.views.user._user import customer_login_helper, user_login_helper


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
        return user_login_helper(self, request, pk=None)
