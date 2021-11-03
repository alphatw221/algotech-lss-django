from rest_framework import viewsets
from ..models.user import User, UserSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, IsAuthenticated)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    # filterset_fields = []
    