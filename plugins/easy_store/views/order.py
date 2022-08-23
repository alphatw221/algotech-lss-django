from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
import service


from automation import jobs

PLUGIN_EASY_STORE = 'easy_store'
class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.order.order.Order.objects.none()

    @action(detail=False, methods=['POST'], url_path=r'webhook/create', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_create_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'webhook/update', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_create_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'webhook/cancel', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_create_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'webhook/paid', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_create_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'webhook/partially_fulfilled', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_create_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)


