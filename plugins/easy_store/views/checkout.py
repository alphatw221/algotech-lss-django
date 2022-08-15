from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
import service


from automation import jobs

PLUGIN_EASY_STORE = 'easy_store'
class CartViewSet(viewsets.ModelViewSet):
    queryset = models.order.pre_order.PreOrder.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'gateway/(?P<cart_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_easy_store_checkout_gateway(self, request, cart_oid):

        #   TODO 
        #   if easy_store checkout not exists:
        #       create
        #   else:
        #       update
        #
        #
        #

        # pre_order = lib.util.verify.Verify.get_pre_order_with_oid(cart_oid)    #temp
        # meta_data = {'easy_store':{
        #                     "checkout_id":'',
        #                     "url":'',
        #                 }}
        
        # pre_order.meta.update(meta_data)
        # pre_order.save()

        return Response('url_here', status=status.HTTP_200_OK)
