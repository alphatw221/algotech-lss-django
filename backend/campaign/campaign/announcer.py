
from typing import Callable

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_lucky_draw import CampaignLuckyDraw
from api.models.campaign.campaign_product import CampaignProduct
from api.models.facebook.facebook_page import FacebookPage
from backend.i18n.campaign_announcement import (
    i18n_get_campaign_announcement_lucky_draw_winner,
    i18n_get_campaign_announcement_product_closed,
    i18n_get_campaign_announcement_product_sold_out)
from backend.message_sending.facebook.campaign_announcement import \
    CampaignAnnouncementFacebookMessageAgent as FacebookMessageAgent


class CampaignAnnouncerError(Exception):
    """Error when announceing Campaign messages."""


class CampaignAnnouncer:
    @staticmethod
    def announce_campaign_product_sold_out(campaign_product: CampaignProduct):
        return CampaignAnnouncer._make_announcement(
            campaign_product.campaign,
            i18n_func=i18n_get_campaign_announcement_product_sold_out,
            args=(campaign_product.order_code,)
        )

    @staticmethod
    def announce_campaign_product_activate(campaign_product: CampaignProduct):
        return
        # * There's no message for this action so return immediately.
        CampaignAnnouncer._make_announcement(
            campaign_product.campaign,
            i18n_func=None,
        )

    @staticmethod
    def announce_campaign_product_deactivate(campaign_product: CampaignProduct):
        return CampaignAnnouncer._make_announcement(
            campaign_product.campaign,
            i18n_func=i18n_get_campaign_announcement_product_closed,
            args=(campaign_product.order_code,)
        )

    @staticmethod
    def announce_lucky_draw_winner(campaign_lucky_draw: CampaignLuckyDraw, customer_name: str):
        return CampaignAnnouncer._make_announcement(
            campaign_lucky_draw.campaign,
            i18n_func=i18n_get_campaign_announcement_lucky_draw_winner,
            args=(campaign_lucky_draw.prize_campaign_product.name, customer_name)
        )

    @staticmethod
    def _make_announcement(campaign: Campaign, i18n_func: Callable, args: tuple):
        if not campaign:
            CampaignAnnouncerError('Campagin not found.')

        result = {}
        if (facebook_page := campaign.facebook_page) and campaign.facebook_campaign:
            text = i18n_func(*args, lang=facebook_page.lang)
            result['text'] = text
            result['facebook'] = CampaignAnnouncer._facebook_announcement(
                facebook_page, campaign.facebook_campaign, text)
        return result

    @staticmethod
    def _facebook_announcement(facebook_page: FacebookPage, facebook_campaign: dict, message_text: str):
        if not facebook_page.token and not facebook_campaign['post_id']:
            raise CampaignAnnouncerError('Missing page_token or post_id')

        return FacebookMessageAgent.page_comment_on_post(
            facebook_page.token, facebook_campaign['post_id'], message_text)