from django.contrib.auth.models import User as AuthUser


from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated





from api import models
import service
import lib
import pendulum
import database
from automation import jobs

class BusinessPolicyViewSet(viewsets.GenericViewSet):
    queryset = AuthUser.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'subscription-plan', permission_classes=(),  authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_subscription_plan(self, request):

        
        return Response("", status=status.HTTP_200_OK)


        #temp