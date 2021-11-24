from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializer
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage
from datetime import datetime


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = UserSubscription.objects.all().order_by('id')
    serializer_class = UserSubscriptionSerializer
    filterset_fields = []
