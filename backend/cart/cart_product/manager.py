from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct
from api.utils.orm import cart_product as orm_cart_product


class CartProductManager:
    NO_DUPLICATE_TYPES = ('order_code', 'cart')

    @staticmethod
    def update_or_create_cart_product(campaign: Campaign,
                                      campaign_product: CampaignProduct,
                                      campaign_comment: CampaignComment,
                                      qty: int, order_code: str, platform: str,
                                      customer_id: str, customer_name: str,
                                      type: str, status: str):
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
            }
        )

    @staticmethod
    def get_last_valid_cart_product(campaign: Campaign,
                                    campaign_product: CampaignProduct,
                                    customer_id: str):
        return orm_cart_product.filter_last_cart_product(
            campaign,
            campaign_product,
            CartProductManager.NO_DUPLICATE_TYPES,
            'valid',
            customer_id
        )

    @staticmethod
    def update_cart_product_qty(cart_product: CartProduct,
                                qty: int):
        orm_cart_product.update_cart_product_qty(cart_product, qty)
