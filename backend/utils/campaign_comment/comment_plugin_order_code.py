from dataclasses import dataclass
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct
from backend.utils.cart_product.request import CartProductRequest
from backend.utils.cart_product.request_processor import CartProductRequestProcessor
from backend.utils.text_processing._text_processor import TextProcessor


@dataclass
class CommentPluginOrderCode():
    @staticmethod
    def process(text_processor: TextProcessor,
                cart_product_request_processor: CartProductRequestProcessor,
                comment: str, order_codes_mapping: dict[str, CampaignProduct]):
        if cart_product_request := CommentPluginOrderCode._get_orders_from_comment(
                text_processor, comment, order_codes_mapping):
            cart_product_request_processor.process(cart_product_request)

    @staticmethod
    def _get_orders_from_comment(text_processor: TextProcessor,
                                 comment: CampaignComment,
                                 order_codes_mapping: dict[str, CampaignProduct]):
        cart_product_request = None
        text = comment.message.lower()

        for order_code, campaign_product in order_codes_mapping.items():
            if qty := text_processor.process(text, order_code):
                if not cart_product_request:
                    cart_product_request = CartProductRequest(comment)

                cart_product_request.add_item(
                    campaign_product, qty, order_code)

        return cart_product_request
