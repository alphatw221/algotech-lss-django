from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.user.user_group import UserGroup, UserGroupSerializer


class UserGroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = UserGroup.objects.all().order_by('id')
    serializer_class = UserGroupSerializer
    filterset_fields = []
