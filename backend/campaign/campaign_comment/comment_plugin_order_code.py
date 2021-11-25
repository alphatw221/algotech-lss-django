from dataclasses import dataclass

from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct
from backend.cart.cart_product.request import CartProductRequest
from backend.cart.cart_product.request_processor import \
    CartProductRequestProcessor
from backend.cart.cart_product.request_responder import \
    CartProductRequestResponder
from backend.cart.cart_product.request_validator import \
    CartProductRequestValidator
from backend.utils.text_processing._text_processor import TextProcessor


@dataclass
class CommentPluginOrderCode():
    @staticmethod
    def process(text_processor: TextProcessor,
                comment: CampaignComment, order_codes_mapping: dict[str, CampaignProduct],
                response_tasks: list,
                cprv: CartProductRequestValidator,
                cprp: CartProductRequestProcessor,
                cprr: CartProductRequestResponder):
        if cart_product_request := CommentPluginOrderCode._get_orders_from_comment(
                text_processor, comment, order_codes_mapping):
            cprv.process(cart_product_request)
            cprp.process(cart_product_request)
            cprr.process(cart_product_request)

            comment.meta['CommentPluginOrderCode'] = cart_product_request.get_items_repr()

            if task := cart_product_request.response_task:
                response_tasks.append(task)

    @staticmethod
    def _get_orders_from_comment(text_processor: TextProcessor,
                                 comment: CampaignComment, order_codes_mapping: dict[str, CampaignProduct]):
        cart_product_request = None
        text = comment.message.lower()

        for order_code, campaign_product in order_codes_mapping.items():
            if (qty := text_processor.process(text, order_code)) is not None:
                if not cart_product_request:
                    cart_product_request = CartProductRequest(comment)

                cart_product_request.add_item(
                    campaign_product, qty)

        return cart_product_request
