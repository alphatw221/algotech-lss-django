from platform import platform
import random
from dataclasses import dataclass

import pendulum
from django.db.utils import DatabaseError
from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_lucky_draw import CampaignLuckyDraw
from api.models.campaign.campaign_product import CampaignProduct
from api.models.order import pre_order
from api.models.order.pre_order import PreOrder
from api.utils.orm import campaign_lucky_draw
from api.views.order.pre_order import PreOrderHelper
from backend.campaign.campaign.announcer import (CampaignAnnouncer,
                                                 CampaignAnnouncerError)
from backend.campaign.campaign_lucky_draw.event import CampaignLuckyDrawEvent
from backend.cart.cart_product.request import CartProductRequest, RequestState
from backend.cart.cart_product.request_processor import \
    CartProductRequestProcessorLuckyDraw
from backend.cart.cart_product.request_validator import \
    CartProductRequestValidatorLuckyDraw
from backend.pymongo.mongodb import db


class CampaignLuckyDrawManager:
    @staticmethod
    def process(campaign: Campaign, event: CampaignLuckyDrawEvent,
                prize_campaign_product: CampaignProduct, num_of_winner: int):

        #create lucky_draw instance        
        lucky_draw = CampaignLuckyDrawProcessor(
            campaign, event,
            prize_campaign_product, num_of_winner
        ).process()

        #add lucky_draw_product add to cart
        # cart_product_requests = CampaignLuckyDrawManager._get_cart_product_requests(
        #     lucky_draw, campaign, prize_campaign_product)
        # cart_product_requests, response_result = CampaignLuckyDrawManager._handle_cart_product_requests(
        #     lucky_draw, event, cart_product_requests)

        response_result = []
        print ('lucky_draw------------')
        print (lucky_draw.__dict__)
        if (len(lucky_draw.winner_list) == 0):
            return lucky_draw
        for winner in lucky_draw.winner_list:
            _json = {}
            try:
                pre_order, created = PreOrder.objects.get_or_create(campaign=campaign, platform=winner[0], customer_id=winner[1], customer_name=winner[2])
                PreOrderHelper.add_product(None, pre_order=pre_order, campaign_product=prize_campaign_product, qty=1)
                result = CampaignAnnouncer.announce_lucky_draw_winner(lucky_draw, winner[2])
                response_result.append(result)
                lucky_draw.meta['announcement_history'] = {
                    'time': pendulum.now('UTC'),
                    'response_result': response_result
                }
                lucky_draw.save()
            except Exception as e:
                print (e)

        return lucky_draw

    @staticmethod
    def _handle_cart_product_requests(lucky_draw: CampaignLuckyDraw, event: CampaignLuckyDrawEvent,
                                      cart_product_requests: list):
        response_result = []
        for cart_product_request in cart_product_requests:
            cprv = CartProductRequestValidatorLuckyDraw()
            cprp = CartProductRequestProcessorLuckyDraw(
                check_inv=True, cart_product_type=event.get_condition_type())
            cprv.process(cart_product_request)
            cprp.process(cart_product_request)

            for item in cart_product_request.get_items():
                if item.state == RequestState.ADDED:
                    try:
                        result = CampaignAnnouncer.announce_lucky_draw_winner(
                            lucky_draw, cart_product_request.customer_name)
                        response_result.append(result)
                    except CampaignAnnouncerError:
                        raise
                elif item.state == RequestState.INSUFFICIENT_INV:
                    ...
                elif item.state == RequestState.INVALID_NEGATIVE_QTY:
                    ...
        return cart_product_requests, response_result

    @staticmethod
    def _get_cart_product_requests(lucky_draw: CampaignLuckyDraw,
                                   campaign: Campaign, prize_campaign_product: CampaignProduct):
        cart_product_requests = []
        for winner in lucky_draw.winner_list:
            cart_product_request = CartProductRequest(campaign, None,
                                                      winner[0], winner[1], winner[2])
                                                      #platfrom_name, platform_id, platform_name
            cart_product_request.add_item(prize_campaign_product, 1)
            cart_product_requests.append(cart_product_request)
        return cart_product_requests


@dataclass
class CampaignLuckyDrawProcessor:
    campaign: Campaign
    event: CampaignLuckyDrawEvent
    prize_campaign_product: CampaignProduct
    num_of_winner: int

    def process(self) -> CampaignLuckyDraw:
        candidate_set = self.event.get_candidate_set()
        try:
            if self.num_of_winner > len(candidate_set):
                self.num_of_winner = len(candidate_set)
            winner_list = random.sample(candidate_set, self.num_of_winner)
        except Exception:
            winner_list = []

        return campaign_lucky_draw.create_campaign_lucky_draw(
            campaign=self.campaign,
            prize_campaign_product=self.prize_campaign_product,
            source_id=self.event.get_source_id(),
            source_type=self.event.get_source_type(),
            condition=self.event.get_condition(),
            condition_type=self.event.get_condition_type(),
            num_of_winner=self.num_of_winner,
            candidate_list=list(candidate_set),
            winner_list=winner_list)
