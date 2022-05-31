
from django.core.files.base import ContentFile
from django.contrib.auth.models import User as AuthUser

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser


import  base64

import service
import lib


class PaymentViewSet(viewsets.GenericViewSet):
    queryset = AuthUser.objects.none()

    @action(detail=False, methods=['PUT'], url_path=r'receipt/upload', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def upload_transfer_receipt(self, request):
        order_id, last_five_digit, image = lib.util.getter.getdata(request,('order_id', 'last_five_digit', 'image'), required = True) 
        
        return Response({"message": "upload succeed"}, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['GET'], url_path=r'stripe/gateway', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_stripe_gateway(self, request):
        order_id, = lib.util.getter.getdata(request,('order_id',), required = True) 
        
        return Response({"url": "http://test.test.com"}, status=status.HTTP_200_OK)
