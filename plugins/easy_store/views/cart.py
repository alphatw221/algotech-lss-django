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

        recaptcha_token, = lib.util.getter.getparams(request, ('recaptcha_token',), with_user=False)
        
        code, response = service.recaptcha.recaptcha.verify_token(recaptcha_token)

        if code!=200 or not response.get('success'):
            raise lib.error_handle.error.api_error.ApiVerifyError('Please Refresh The Page And Retry Again')

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(cart_oid)    #temp

        campaign_product_dict = {str(campaign_product.id):campaign_product for campaign_product in pre_order.campaign.products.all()}
        # pre_order.campaign.user_subscription...

        # line_items = []
        # for campaign_product_id_str,product in pre_order.products:
        #   if campaign_product_id_str not in campaign_product_dict:
        #       continue
        #   campaign_product = campaign_product_dict[campaign_product_id_str]
        #   line_items.append({'variant_id':campaign_product.meta.get('easy_store',{}).get('variant_id'), 'quantity':product.get('qty')})
        # 
        #     
        #   TODO 
        #   if easy_store checkout not exists:
        #       create
        #   else:
        #       update
        #
        #
        #

        
        # meta_data = {'easy_store':{
        #                     "checkout_id":'',
        #                     "url":'',
        #                 }}
        
        # pre_order.meta.update(meta_data)
        # pre_order.save()

        return Response('url_here', status=status.HTTP_200_OK)
