from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.utils.orm.campaign_comment import get_campaign_comments
from backend.campaign.campaign_comment.command_responder import \
    CampaginCommentResponderCommand
from backend.campaign.campaign_comment.comment_plugin_command import \
    CommentPluginCommand
from backend.campaign.campaign_comment.comment_plugin_order_code import \
    CommentPluginOrderCode
from backend.campaign.campaign_product.manager import CampaignProductManager
from backend.campaign.campaign_product.status_processor import \
    CampaignProductStatusProcessor
from backend.cart.cart_product.request_processor import \
    CartProductRequestProcessorStandard
from backend.cart.cart_product.request_responder import \
    CartProductRequestResponderOrderCode
from backend.cart.cart_product.request_validator import \
    CartProductRequestValidatorStandard
from backend.utils.text_processing.command_processor import \
    CommandTextProcessor
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

        self.campaign_product_status = 1 if self.campaign.ordering_only_activated_products else None
        self.order_codes_mapping = {}
        if self.enable_order_code:
            self.order_codes_mapping = CampaignProductManager.get_order_codes_mapping(
                self.campaign, status=self.campaign_product_status, lower=True)

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
            if not self._plugin_command(comment):
                self._plugin_order_code(comment)
            self._mark_and_save_comment(comment)

        if self.unprocessed_comments:
            self._process_campaign_products()
            self._process_batch_tasks()

        return f'{len(self.unprocessed_comments)=}'

    def _plugin_command(self, comment: CampaignComment):
        tp = CommandTextProcessor
        ccr = CampaginCommentResponderCommand(self.response_platforms)
        return CommentPluginCommand.process(tp, comment,
                                            self.batch_tasks_list, ccr)

    

    def _plugin_order_code(self, comment: CampaignComment):
        tp = OrderCodeTextProcessor
        cprv = CartProductRequestValidatorStandard()
        cprp = CartProductRequestProcessorStandard(
            check_inv=True, cart_product_type='order_code')
        cprr = CartProductRequestResponderOrderCode(self.response_platforms)
        return CommentPluginOrderCode.process(self.campaign,
                                              tp, comment, self.order_codes_mapping,
                                              self.batch_tasks_list, cprv, cprp, cprr)

    def _plugin_order_code_rq(self, comment: CampaignComment):
        tp = OrderCodeTextProcessor
        cprv = CartProductRequestValidatorStandard()
        cprp = CartProductRequestProcessorStandard(
            check_inv=True, cart_product_type='order_code')
        cprr = CartProductRequestResponderOrderCode(self.response_platforms)
        return CommentPluginOrderCode.process(self.campaign,
                                              tp, comment, self.order_codes_mapping,
                                              self.batch_tasks_list, cprv, cprp, cprr)


    def _mark_and_save_comment(self, comment: CampaignComment):
        comment.status = 1
        comment.save()

    def _process_campaign_products(self):
        for campaign_product in CampaignProductManager.get_campaign_products(
                self.campaign, status=self.campaign_product_status):
            if campaign_product.status == 1 and \
                    campaign_product.qty_sold >= campaign_product.qty_for_sale:
                task = CampaignProductStatusProcessor.get_campaign_product_sold_out_task(
                    campaign_product)
                self.batch_tasks_list.insert(0, task)

    def _process_batch_tasks(self):
        with ThreadPoolExecutor(max_workers=self.max_response_workers) as executor:
            for batch_task in self.batch_tasks_list:
                executor.submit(batch_task)



@dataclass
class RQCommentProcessor:
    campaign: Campaign
    campaign_comment: CampaignComment
    order_codes_mapping: dict = {}
    enable_order_code: bool = True
    response_platforms: list = field(default_factory=list)
    

    def __post_init__(self):
        # self.unprocessed_comments = get_campaign_comments(
        #     self.campaign, status=0, order_by='pk', limit=self.comment_batch_size)

        # self.campaign_product_status = 1 if self.campaign.ordering_only_activated_products else None
        # self.order_codes_mapping = {}
        # if self.enable_order_code:
        #     self.order_codes_mapping = CampaignProductManager.get_order_codes_mapping(
        #         self.campaign, status=self.campaign_product_status, lower=True)

        tmp_response_platforms = {}
        for platform in self.response_platforms:
            if platform == 'facebook' and self.campaign.facebook_page:
                tmp_response_platforms['facebook'] = self.campaign.facebook_page
            elif platform == 'youtube' and self.campaign.youtube_channel:
                tmp_response_platforms['youtube'] = self.campaign.youtube_channel
        self.response_platforms = tmp_response_platforms

    def process(self):
        if not self._rq_plugin_command():
            self._rq_plugin_order_code()
        self._rq_mark_and_save_comment()

        if self.unprocessed_comments:
            self._process_campaign_products()
            self._process_batch_tasks()

        return f'{len(self.unprocessed_comments)=}'

    def _rq_plugin_command(self):
        tp = CommandTextProcessor
        ccr = CampaginCommentResponderCommand(self.response_platforms)
        command = tp.process(self.campaign_comment.message)
        if not command:
            return None

        self.campaign_comment.meta['CommentPluginCommand'] = f'{command!r}'
        if task := ccr.process(self.campaign_comment, command):
            task.process()
            return True

    def _rq_plugin_order_code(self):
        tp = OrderCodeTextProcessor
        cprv = CartProductRequestValidatorStandard()
        cprp = CartProductRequestProcessorStandard(
            check_inv=True, cart_product_type='order_code')
        cprr = CartProductRequestResponderOrderCode(self.response_platforms)
        # return CommentPluginOrderCode.process(self.campaign,
        #                                       tp, comment, self.order_codes_mapping,
        #                                       self.batch_tasks_list, cprv, cprp, cprr)
        
        if CommentPluginOrderCode._if_to_ignore(self.campaign, self.campaign_comment):
            return

        if cart_product_request := CommentPluginOrderCode._get_cart_product_request(
                self.campaign, tp, self.campaign_comment, self.order_codes_mapping):
            cprv.process(cart_product_request)
            cprp.process(cart_product_request)
            cprr.process(cart_product_request)

        self.campaign_comment.meta['CommentPluginOrderCode'] = cart_product_request.get_items_repr()

        if task := cart_product_request.response_task:
            task.process()
            return True

    def _rq_mark_and_save_comment(self):
        self.campaign_comment.status = 1
        self.campaign_comment.comment.save()

    