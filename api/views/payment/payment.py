from rest_framework import views, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from django.conf import settings

from django.core.files.storage import default_storage



class PaymentViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    permission_classes = [IsAdminUser | IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def test(self, request, *args, **kwargs):
        return Response({'msg': 'TestViewSet test accomplished.'})