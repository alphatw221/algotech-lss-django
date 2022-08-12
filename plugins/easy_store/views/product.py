from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
import service

# from .. import job as easy_store_job
from automation import jobs

PLUGIN_EASY_STORE = 'easy_store'
class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.product.product.Product.objects.all()

    @action(detail=False, methods=['GET'], url_path=r'export', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def export_product_from_easy_store(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        credential = user_subscription.user_plan.get('plugins',{}).get(PLUGIN_EASY_STORE)
        if not credential:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_plugin')
        
        service.rq.queue.enqueue_general_queue(jobs.easy_store.export_product_job, user_subscription_id = user_subscription.id, credential=credential)
        return Response('ok', status=status.HTTP_200_OK)
