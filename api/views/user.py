from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from api.models.user.user import User, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, IsAuthenticated)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = []
