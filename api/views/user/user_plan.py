from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.user.user_plan import UserPlan, UserPlanSerializer


class UserPlanViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = UserPlan.objects.all().order_by('id')
    serializer_class = UserPlanSerializer
    filterset_fields = []
