import pendulum
from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct
from api.utils.orm import cart_product as orm_cart_product
from django.db import transaction


class CartProductManager:
    NO_DUPLICATE_TYPES = ('order_code', 'cart')

    @staticmethod
    def create_cart_product(campaign: Campaign,
                            campaign_product: CampaignProduct,
                            campaign_comment: CampaignComment,
                            qty: int, order_code: str,
                            platform: str, customer_id: str, customer_name: str,
                            type: str = 'n/a', status: str = 'valid',
                            remark: str = None):
        return orm_cart_product.create_cart_product(
            campaign,
            campaign_product,
            campaign_comment,
            qty, order_code,
            platform, customer_id, customer_name,
            type, status,
            remark, {
                'history': [{
                    'time': pendulum.now('UTC'),
                    'qty': qty,
                }]}
        )

    @staticmethod
    def update_or_create_cart_product(campaign: Campaign,
                                      campaign_product: CampaignProduct,
                                      campaign_comment: CampaignComment,
                                      qty: int, order_code: str, platform: str,
                                      customer_id: str, customer_name: str,
                                      type: str, status: str,
                                      remark: str = None):
        return orm_cart_product.update_or_create_cart_product(
            campaign,
            campaign_product,
            campaign_comment,
            {
                'qty': qty,
                'order_code': order_code,
                'platform': platform,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'type': type,
                'status': status,
                'remark': remark,
                'meta': {
                    'history': [{
                        'time': pendulum.now('UTC'),
                        'qty': qty,
                    }]}
            }
        )

    @staticmethod
    def get_last_valid_cart_product(campaign: Campaign,
                                    campaign_product: CampaignProduct,
                                    customer_id: str, platform: str):
        return orm_cart_product.filter_last_cart_product(
            campaign,
            campaign_product,
            CartProductManager.NO_DUPLICATE_TYPES,
            'valid',
            customer_id,
            platform
        )

    @staticmethod
    def update_cart_product_qty(cart_product: CartProduct,
                                qty: int):
        cart_product = CartProduct.objects.select_for_update().get(
            pk=cart_product.pk)
        with transaction.atomic():
            return orm_cart_product.update_cart_product_qty(
                cart_product, qty,
                {
                    'time': pendulum.now('UTC'),
                    'qty': qty,
                }
            )
