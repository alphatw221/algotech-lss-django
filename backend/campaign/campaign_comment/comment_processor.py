from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
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
    comment_batch_size: int = 500
    max_response_workers: int = 10
    enable_order_code: bool = True
    only_activated_order_code: bool = True
    response_platforms: list = field(default_factory=list)

    def __post_init__(self):
        self.unprocessed_comments = get_campaign_comments(
            self.campaign, status=0, order_by='pk', limit=self.comment_batch_size)

        if self.enable_order_code:
            status = 1 if self.only_activated_order_code else None
            self.order_codes_mapping = get_campaign_products_order_codes_mapping(
                self.campaign, status=status, lower=True)
        else:
            self.order_codes_mapping = {}

        response_platforms = {}
        for platform in self.response_platforms:
            if platform == 'facebook' and self.campaign.facebook_page:
                response_platforms['facebook'] = self.campaign.facebook_page
            elif platform == 'youtube' and self.campaign.youtube_channel:
                response_platforms['youtube'] = self.campaign.youtube_channel
        self.response_platforms = response_platforms

        self.response_tasks = []

    def process(self):
        self._process_comment()
        self._process_response_tasks()

        return f'{len(self.unprocessed_comments)=}'

    def _process_comment(self):
        for comment in self.unprocessed_comments:
            self._plugin_order_code(comment)
            self._mark_and_save_comment(comment)

    def _process_response_tasks(self):
        with ThreadPoolExecutor(max_workers=self.max_response_workers) as executor:
            for response_task in self.response_tasks:
                executor.submit(response_task)

    def _plugin_order_code(self, comment: CampaignComment):
        tp = OrderCodeTextProcessor
        cprv = CartProductRequestValidatorRegular()
        cprp = CartProductRequestProcessorRegular(check_inv=True)
        cprr = CartProductRequestResponderRegular(self.response_platforms)
        if response_task := CommentPluginOrderCode.process(tp, comment, self.order_codes_mapping,
                                                           cprv, cprp, cprr):
            self.response_tasks.append(response_task)

    def _mark_and_save_comment(self, comment: CampaignComment):
        comment.status = 1
        comment.save()
