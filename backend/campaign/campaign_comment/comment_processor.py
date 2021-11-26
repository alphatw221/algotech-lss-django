from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.utils.orm.campaign_comment import get_campaign_comments
from api.utils.orm.campaign_product import \
    get_campaign_products_order_codes_mapping
from backend.campaign.campaign_comment.comment_plugin_order_code import \
    CommentPluginOrderCode
from backend.campaign.campaign_product.status_processor import \
    CampaignProductStatusProcessor
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
    comment_batch_size: int = 100
    max_response_workers: int = 10
    enable_order_code: bool = True
    response_platforms: list = field(default_factory=list)

    def __post_init__(self):
        self.unprocessed_comments = get_campaign_comments(
            self.campaign, status=0, order_by='pk', limit=self.comment_batch_size)

        self.order_codes_mapping = {}
        if self.enable_order_code:
            status = 1 if self.campaign.ordering_only_activated_products else None
            self.order_codes_mapping = get_campaign_products_order_codes_mapping(
                self.campaign, status=status, lower=True)

        tmp_response_platforms = {}
        for platform in self.response_platforms:
            if platform == 'facebook' and self.campaign.facebook_page:
                tmp_response_platforms['facebook'] = self.campaign.facebook_page
            elif platform == 'youtube' and self.campaign.youtube_channel:
                tmp_response_platforms['youtube'] = self.campaign.youtube_channel
        self.response_platforms = tmp_response_platforms

        self.batch_tasks_list = []

    def process(self):
        for comment in self.unprocessed_comments:
            self._plugin_order_code(comment)
            self._mark_and_save_comment(comment)

        if self.unprocessed_comments:
            self._process_campaign_products()
            self._process_batch_tasks()

        return f'{len(self.unprocessed_comments)=}'

    def _plugin_order_code(self, comment: CampaignComment):
        tp = OrderCodeTextProcessor
        cprv = CartProductRequestValidatorRegular()
        cprp = CartProductRequestProcessorRegular(check_inv=True)
        cprr = CartProductRequestResponderRegular(self.response_platforms)
        CommentPluginOrderCode.process(self.campaign,
                                       tp, comment, self.order_codes_mapping,
                                       self.batch_tasks_list, cprv, cprp, cprr)

    def _mark_and_save_comment(self, comment: CampaignComment):
        comment.status = 1
        comment.save()

    def _process_campaign_products(self):
        for _, campaign_product in self.order_codes_mapping.items():
            if campaign_product.status == 1 and \
                    campaign_product.qty_sold >= campaign_product.qty_for_sale:
                task = CampaignProductStatusProcessor.get_campaign_product_sold_out_task(
                    campaign_product)
                self.batch_tasks_list.insert(0, task)

    def _process_batch_tasks(self):
        with ThreadPoolExecutor(max_workers=self.max_response_workers) as executor:
            for batch_task in self.batch_tasks_list:
                executor.submit(batch_task)
