from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from backend.cart.cart_product.request import CartProductRequest
from backend.cart.cart_product.request_processor import \
    CartProductRequestProcessorStandard
from backend.cart.cart_product.request_validator import \
    CartProductRequestValidatorStandard


class CartManager:
    @staticmethod
    def create_cart_product_request(campaign: Campaign, platform: str,
                                    customer_id: str, customer_name: str,
                                    items=dict):
        cart_product_request = CartProductRequest(
            campaign, None, platform, customer_id, customer_name)
        for campaign_product, qty in items.items():
            cart_product_request.add_item(campaign_product, qty)
            
        return cart_product_request

    @staticmethod
    def process(cart_product_request: CartProductRequest):
        cprv = CartProductRequestValidatorStandard()
        cprp = CartProductRequestProcessorStandard(
            check_inv=True, cart_product_type='cart')

        cprv.process(cart_product_request)
        cprp.process(cart_product_request)

        return cart_product_request
