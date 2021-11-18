from dataclasses import dataclass
from api.models.campaign.campaign import Campaign
from api.utils.orm.campaign_comment import get_campaign_comments
from api.utils.orm.campaign_product import get_campaign_products_order_codes_mapping
from api.utils.common.text_processing.order_code_processor import OrderCodeProcessor


@dataclass
class CommentProcessor:
    campaign: Campaign

    def __post_init__(self):
        self.unprocessed_comments = get_campaign_comments(
            self.campaign, order_by='pk', limit=2)  # TODO:
        # self.comments = get_campaign_comments(
        #     self.campaign, status=0, order_by='pk', limit=1000)
        self.order_codes_mapping = get_campaign_products_order_codes_mapping(
            self.campaign, lower=True)

    def process(self):
        for comment in self.unprocessed_comments:
            cart_product_requests = OrderCodeProcessor.process(
                comment, self.order_codes_mapping)
            print(cart_product_requests)

            self._mark_comment_processed(comment)
        return f'{len(self.unprocessed_comments)=}'

    def _mark_comment_processed(self, comment):
        comment.status = 1
        comment.save()
