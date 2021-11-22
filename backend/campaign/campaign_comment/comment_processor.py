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

    def __post_init__(self):
        self.unprocessed_comments = get_campaign_comments(
            self.campaign, status=0, order_by='pk', limit=1000)
        self.order_codes_mapping = get_campaign_products_order_codes_mapping(
            self.campaign, lower=True)

    def process(self):
        for comment in self.unprocessed_comments:
            self._process_comment(comment)
            self._mark_comment_processed(comment)

        return f'{len(self.unprocessed_comments)=}'

    def _process_comment(self, comment):
        # TODO: Campaign can be set not to validate cart request, swap out CartProductRequestValidatorRegular
        CommentPluginOrderCode.process(OrderCodeTextProcessor,
                                       comment, self.order_codes_mapping,
                                       CartProductRequestValidatorRegular,
                                       CartProductRequestProcessorRegular,
                                       CartProductRequestResponderRegular)

    def _mark_comment_processed(self, comment):
        comment.status = 1
        comment.save()
