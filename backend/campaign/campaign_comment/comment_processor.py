from dataclasses import dataclass

from api.models.campaign.campaign import Campaign
from api.utils.orm.campaign_comment import get_campaign_comments
from api.utils.orm.campaign_product import \
    get_campaign_products_order_codes_mapping
from backend.campaign.campaign_comment.comment_plugin_order_code import \
    CommentPluginOrderCode
from backend.cart.cart_product.request_processor import \
    CartProductRequestProcessorRegular
from backend.cart.cart_product.request_responder import \
    CartProductRequestResponderRegular
from backend.cart.cart_product.request_validator import \
    CartProductRequestValidatorRegular
from backend.utils.text_processing.order_code_processor import \
    OrderCodeTextProcessor


@dataclass
class CommentProcessor:
    campaign: Campaign
    enable_order_code: bool = True
    only_activated_order_code: bool = True

    def __post_init__(self):
        self.unprocessed_comments = get_campaign_comments(
            self.campaign, status=0, order_by='pk', limit=1000)

        status = 1 if self.only_activated_order_code else None
        self.order_codes_mapping = \
            get_campaign_products_order_codes_mapping(
                self.campaign, status=status, lower=True) \
            if self.enable_order_code \
            else {}

    def process(self):
        for comment in self.unprocessed_comments:
            self._plugin_order_code(comment)
            self._mark_and_save_comment(comment)

        return f'{len(self.unprocessed_comments)=}'

    def _plugin_order_code(self, comment):
        tp = OrderCodeTextProcessor
        cprv = CartProductRequestValidatorRegular()
        cprp = CartProductRequestProcessorRegular(check_inv=True)
        cprr = CartProductRequestResponderRegular()
        result = CommentPluginOrderCode.process(tp, comment, self.order_codes_mapping,
                                                cprv, cprp, cprr)
        comment.meta['CommentPluginOrderCode'] = result

    def _mark_and_save_comment(self, comment):
        comment.status = 1
        comment.save()
