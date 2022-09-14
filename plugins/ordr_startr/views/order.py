from rest_framework import status, viewsets

from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib


from lib.authentication_class.v1_token_authentication import V1PermanentTokenAuthentication
from lib.permission_class.v1_token_permission import IsAuthenticated, IsAuthorizedByUserSubscription

from .. import lib as ordr_startr_lib
import database
PLUGIN_ORDR_STARTR = 'ordr_startr'
from bson.objectid import ObjectId

class OrderViewSet(viewsets.GenericViewSet):
    queryset = models.order.order.Order.objects.none()

    @action(detail=False, methods=['PUT'], url_path=r'callback/(?P<user_subscription_id>[^/.]+)/payment/complete', permission_classes=(IsAuthenticated,IsAuthorizedByUserSubscription), authentication_classes=[V1PermanentTokenAuthentication,])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def order_payment_complete_callback(self, request, user_subscription_id):

        ordr_startr_order_data, ordr_startr_products_data = lib.util.getter.getdata(request,('order', 'products'),required=True)
        print(ordr_startr_order_data)
        lss_pre_order_oid = ordr_startr_order_data.get('ExternalReferenceId')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(lss_pre_order_oid)
        campaign = pre_order.campaign
        if campaign.user_subscription.id != int(user_subscription_id):
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid')
        campaign_product_external_internal_map = ordr_startr_lib.mapping_helper.CampaignProduct.get_external_internal_map(campaign)
        print(campaign_product_external_internal_map)

        lss_order_data = ordr_startr_lib.transformer.to_lss_order(ordr_startr_order_data, pre_order, campaign_product_external_internal_map)

        lss_order = models.order.order.Order.objects.create(**lss_order_data)

        for campaign_product_id_str,product in pre_order.products.items():
            database.lss.campaign_product.CampaignProduct(id = int(campaign_product_id_str)).customer_return(product.get('qty'), sync=False) #do this anyway
        database.lss.pre_order.PreOrder(id=pre_order.id).reset_pre_order(sync=False)            #do this anyway
        database.lss.order_product.OrderProduct.transfer_to_order(pre_order, lss_order)         #do this anyway

        print(ordr_startr_products_data)
        ##update campaign product quantity:
        for product in ordr_startr_products_data:
            if product.get('_id') not in campaign_product_external_internal_map:
                continue
            lss_campaign_product_data = campaign_product_external_internal_map[product.get('_id')]
            pymongo_campaign_product = database.lss.campaign_product.CampaignProduct(id = lss_campaign_product_data.get('id'))
            if lss_campaign_product_data.get('qty_for_sale',0)<=product.get('stock',0):
                pymongo_campaign_product.sold_from_external(qty=product.get('sold',0))
            else:
                qty_sold = lss_campaign_product_data.get('qty_for_sale',0)-product.get('stock',0) 
                pymongo_campaign_product.set_qty_sold(qty=qty_sold, sync=False)

        return Response('ok', status=status.HTTP_200_OK)

        ordr_startr_products_data = [{'maxQty': 5, 'defaultMaxQty': 5, 'SKU': 'NW02', 'visible': True, 'sold': 2, 'supplierName': 'Korea', 'counter': 30, '_id': '6315cc771cd21f3691d51bac', 'description': 'Naomi Card Wallet -Butter (WxH: 4.4"x3.2")', 'keyword': 'NW02', 'price': 230, 'stock': 3, 'reply_message': 'Naomi Card Wallet -Butter (WxH: 4.4"x3.2")', 'FbPageId': '105929794479727', 'createdAt': '2022-09-05T10:16:24.002Z', 'updatedAt': '2022-09-09T10:03:50.990Z', '__v': 0}, {'maxQty': 5, 'defaultMaxQty': 5, 'SKU': 'NW03', 'visible': True, 'sold': 0, 'supplierName': 'Korea', 'counter': 31, '_id': '6315cc771cd21f3691d51bad', 'description': 'Naomi Card Wallet -W.Green (WxH: 4.4"x3.2")', 'keyword': 'NW03', 'price': 230, 'stock': 5, 'reply_message': 'Naomi Card Wallet -W.Green (WxH: 4.4"x3.2")', 'FbPageId': '105929794479727', 'createdAt': '2022-09-05T10:16:24.002Z', 'updatedAt': '2022-09-09T10:03:50.990Z', '__v': 0}]

        # data = {
        #     'FbId': '4422762234485468', 
        #     'Status': 'confirmed', 
        #     'Is_FirstOrder': False, 
        #     'ShippingCharge': 0, 
        #     'PaymentStatus': 'paid', 
        #     'DiscountAmount': 0, 
        #     'PaidAmount': 230, 
        #     'Payment_id': 'payment_aef65717a624d8117d2945edadca65c9', 
        #     'ApplyPoint': 0, 
        #     'DiscountAmountPoint': 0, 
        #     'OrderWisePoint': 460, 
        #     'PaymentClientStatus': 'completed', 
        #     'DeductQtyUponPaymentStatus': '', 
        #     'ReferralCode': '', 
        #     'OrcCode': '', 
        #     'HideDeliveryMessage': 
        #     'Supplier will contact you within 5 working days to arrange delivery with you. \xf0\x9f\x99\x82', 
        #     'RemarkMessage': 'Remark Message', 
        #     'FeedBackMessage': '', 
        #     'ExternalReferenceId': '631ec4112db8f9159224c78a', 
        #     '_id': '631eca8930c53159c9cbed8e', 
        #     'FbPageId': '105929794479727', 
        #     'sourceType': 'FB', 
        #     'Date': '2022-09-12T05:58:40.000Z', 
        #     'DeliveryTimeSlot': None, 
        #     'Items': [{'_id': '631eca9030c53159c9cbed92', 'id': '6315cc771cd21f3691d51bad', 'itemName': 'Naomi Card Wallet -W.Green (WxH: 4.4"x3.2")', 'qty': 1, 'price': 230, 'keyword': 'NW03', 'SKU': 'NW03', 'total': 230, 'supplierName': 'Korea', 'Date': '2022-09-12T05:58:40.000Z'}], 'Name': 'Yi-Hsueh Lin', 'Residential_Type': 'HDB', 'ShippingAddress1': '1234', 'ShippingEmail': 'asdfasdf', 'ShippingMobile': '1234', 'ShippingName': 'Yi-Hsueh Lin', 'ShippingPostalCode': '1234', 'ShippingSupplier': [], 'Total': 230, '__v': 0, 'createdAt': '2022-09-12T05:58:33.684Z', 'updatedAt': '2022-09-12T05:59:32.216Z', 'MisMatchItems': [], 'ValidItems': [], 'ShippingAddress2': None, 'PaymentDate': '2022-09-12T05:59:32.000Z'}
        # map = {'6315cc771cd21f3691d51bad': {'id': 9393, 'name': 'NW03', 'image': 'https://storage.googleapis.com/lss_public_bucket/static/no_image.jpeg', 'type': 'product'}, '6315cc771cd21f3691d51bac': {'id': 9394, 'name': 'NW02', 'image': 'https://storage.googleapis.com/lss_public_bucket/static/no_image.jpeg', 'type': 'product'}}





        # data = {
        #     'FbId': '4422762234485468', 
        #     'Status': 'confirmed', 
        #     'Is_FirstOrder': False, 
        #     'ShippingCharge': 0, 'PaymentStatus': 'paid', 'DiscountAmount': 0, 
        #     'PaidAmount': 230, 'Payment_id': 'payment_ba95947116bc3b114059816fecbf8b01', 
        #     'ApplyPoint': 0, 'DiscountAmountPoint': 0, 'OrderWisePoint': 460, 
        #     'PaymentClientStatus': 'completed', 'DeductQtyUponPaymentStatus': '', 
        #     'ReferralCode': '', 'OrcCode': '', 
        #     'HideDeliveryMessage': 'Supplier will contact you within 5 working days to arrange delivery with you. \xf0\x9f\x99\x82', 
        #     'RemarkMessage': 'Remark Message', 'FeedBackMessage': '', 'ExternalReferenceId': 
        #     '631ec4112db8f9159224c78a', '_id': '631ecc7630c53159c9cbed96', 'FbPageId': '105929794479727', 'sourceType': 'FB', 
        #     'Date': '2022-09-12T06:06:46.000Z', 'DeliveryTimeSlot': None, 
        #     'Items': [{'_id': '631ecc7630c53159c9cbed97', 'id': '6315cc771cd21f3691d51bac', 'itemName': 'Naomi Card Wallet -Butter (WxH: 4.4"x3.2")', 'qty': 1, 'price': 230, 'keyword': 'NW02', 'SKU': 'NW02', 'total': 230, 'supplierName': 'Korea', 'Date': '2022-09-12T06:06:46.000Z'}], 'Name': 'Yi-Hsueh Lin', 'Residential_Type': 'HDB', 'ShippingAddress1': 'asdf', 'ShippingEmail': 'asdfasdf', 'ShippingMobile': '1234', 'ShippingName': 'Yi-Hsueh Lin', 'ShippingPostalCode': '12', 'ShippingSupplier': [], 'Total': 230, '__v': 0, 'createdAt': '2022-09-12T06:06:46.032Z', 'updatedAt': '2022-09-12T06:07:34.181Z', 'MisMatchItems': [], 'ValidItems': [], 'ShippingAddress2': None, 'PaymentDate': '2022-09-12T06:07:34.000Z'}
        # map =  {'6315cc771cd21f3691d51bad': {'id': 9393, 'name': 'NW03', 'image': 'https://storage.googleapis.com/lss_public_bucket/static/no_image.jpeg', 'type': 'product'}, '6315cc771cd21f3691d51bac': {'id': 9394, 'name': 'NW02', 'image': 'https://storage.googleapis.com/lss_public_bucket/static/no_image.jpeg', 'type': 'product'}}

        # Items= [{'_id': '631ecf0b30c53159c9cbedb1', 'id': '6315cc771cd21f3691d51bac', 'itemName': 'Naomi Card Wallet -Butter (WxH: 4.4"x3.2")', 'qty': 1, 'price': 230, 'keyword': 'NW02', 'SKU': 'NW02', 'total': 230, 'supplierName': 'Korea', 'Date': '2022-09-12T06:17:47.000Z'}, {'_id': '631ecf0b30c53159c9cbedb2', 'id': '6315cc771cd21f3691d51bad', 'itemName': 'Naomi Card Wallet -W.Green (WxH: 4.4"x3.2")', 'qty': 1, 'price': 230, 'keyword': 'NW03', 'SKU': 'NW03', 'total': 230, 'supplierName': 'Korea', 'Date': '2022-09-12T06:17:47.000Z'}]