from api.models.campaign.campaign import Campaign
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


class CommentPluginOrderCode():
    @staticmethod
    def process(campaign: Campaign,
                text_processor: TextProcessor,
                comment: CampaignComment, order_codes_mapping: dict[str, CampaignProduct],
                batch_tasks_list: list,
                cprv: CartProductRequestValidator,
                cprp: CartProductRequestProcessor,
                cprr: CartProductRequestResponder):
        if CommentPluginOrderCode._if_to_ignore(campaign, comment):
            return

        if cart_product_request := CommentPluginOrderCode._get_cart_product_request(
                campaign, text_processor, comment, order_codes_mapping):
            cprv.process(cart_product_request)
            cprp.process(cart_product_request)
            cprr.process(cart_product_request)

            comment.meta['CommentPluginOrderCode'] = cart_product_request.get_items_repr()

            if task := cart_product_request.response_task:
                batch_tasks_list.append(task)

    @staticmethod
    def _if_to_ignore(campaign: Campaign, comment: CampaignComment):
        if comment.platform == 'facebook' and (facebook_page := campaign.facebook_page):
            if comment.customer_id == facebook_page.page_id:
                return True
        return False

    @staticmethod
    def _get_cart_product_request(campaign: Campaign, text_processor: TextProcessor,
                                  comment: CampaignComment, order_codes_mapping: dict[str, CampaignProduct]):
        cart_product_request = None
        text = comment.message.lower()

        for order_code, campaign_product in order_codes_mapping.items():
            if (qty := text_processor.process(text, order_code)) is not None:
                if not cart_product_request:
                    cart_product_request = CartProductRequest(
                        campaign, comment, comment.platform, comment.customer_id, comment.customer_name)

                cart_product_request.add_item(
                    campaign_product, qty)

        return cart_product_request
