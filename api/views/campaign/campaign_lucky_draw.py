from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models.campaign.campaign_lucky_draw import (
    CampaignLuckyDraw, CampaignLuckyDrawSerializer)
from api.models.campaign.campaign_lucky_draw import CampaignLuckyDraw
from api.utils.common.verify import Verify
from api.utils.common.common import *

from backend.campaign.campaign_lucky_draw.manager import CampaignLuckyDrawManager
from backend.campaign.campaign_lucky_draw.event import DrawFromCampaignLikesEvent, DrawFromCampaignCommentsEvent, DrawFromCartProductsEvent, DrawFromProductsEvent


def verify_request(api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id, campaign_product_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)
    prize_campaign_product = Verify.get_campaign_product(
        campaign, prize_campaign_product_id)

    if campaign_product_id:
        campaign_product_id = Verify.get_campaign_product(
            campaign, campaign_product_id)
        return platform, campaign, prize_campaign_product, campaign_product_id

    return platform, campaign, prize_campaign_product


def get_winner_json(winner_lists):
    response_list = []
    for winner_list in winner_lists:
        winner = {}
        winner['platform'] = winner_list[0]
        winner['customer_id'] = winner_list[1]
        winner['customer_name'] = winner_list[2]
        response_list.append(winner)

    response_json = {
        'winner_list': response_list
    }
    return response_json


class CampaignLuckyDrawViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CampaignLuckyDraw.objects.all().order_by('id')
    serializer_class = CampaignLuckyDrawSerializer
    filterset_fields = []

    # lucky_draw = CampaignLuckyDrawManager.process(
    #     c, DrawFromCampaignLikesEvent(c), prize_cp, 1,
    # )

    # lucky_draw = CampaignLuckyDrawManager.process(
    #     c, DrawFromCampaignCommentsEvent(c, 'order'), prize_cp, 1,
    # )

    # lucky_draw = CampaignLuckyDrawManager.process(
    #     c, DrawFromCartProductsEvent(c, cp), prize_cp, 1,
    # )
    @action(detail=False, methods=['GET'], url_path=r'list_winner')
    @api_error_handler
    def list_winner(self, request):
        campaign_id = request.query_params.get('campaign_id')
        winner_list = CampaignLuckyDraw.objects.filter(campaign_id=campaign_id)

        return Response(winner_list, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'likes')
    @api_error_handler
    def lucky_draw_likes(self, request):
        api_user, platform_id, platform_name, campaign_id, prize_campaign_product_id, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "prize_campaign_product_id", "qty")
        )
        qty = int(qty)
        api_user = request.user.api_users.get(type='user')

        _, campaign, prize_campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id)

        lucky_draw = CampaignLuckyDrawManager.process(
            campaign, DrawFromCampaignLikesEvent(
                campaign), prize_campaign_product, qty,
        )
        response_json = get_winner_json(lucky_draw.winner_list)

        return Response(response_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'comment')
    @api_error_handler
    def lucky_draw_comment(self, request):
        api_user, platform_id, platform_name, campaign_id, prize_campaign_product_id, keyword, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "prize_campaign_product_id", "keyword", "qty")
        )
        qty = int(qty)
        api_user = request.user.api_users.get(type='user')

        _, campaign, prize_campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id)

        lucky_draw = CampaignLuckyDrawManager.process(
            campaign, DrawFromCampaignCommentsEvent(
                campaign, keyword), prize_campaign_product, qty,
        )
        response_json = get_winner_json(lucky_draw.winner_list)

        return Response(response_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'carts')
    @api_error_handler
    def lucky_draw_cart(self, request):
        api_user, platform_id, platform_name, campaign_id, prize_campaign_product_id, campaign_product_id, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "prize_campaign_product_id", "campaign_product_id", "qty")
        )
        qty = int(qty)
        api_user = request.user.api_users.get(type='user')

        _, campaign, prize_campaign_product, campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id, campaign_product_id = campaign_product_id)

        lucky_draw = CampaignLuckyDrawManager.process(
            campaign, DrawFromCartProductsEvent(
                campaign, campaign_product), prize_campaign_product, qty,
        )
        response_json = get_winner_json(lucky_draw.winner_list)

        return Response(response_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'products')
    @api_error_handler
    def lucky_draw_products(self, request):
        api_user, platform_id, platform_name, campaign_id, prize_campaign_product_id, campaign_product_id, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "prize_campaign_product_id", "campaign_product_id", "qty")
        )
        qty = int(qty)
        api_user = request.user.api_users.get(type='user')

        _, campaign, prize_campaign_product, campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id, campaign_product_id = campaign_product_id)

        lucky_draw = CampaignLuckyDrawManager.process(
            campaign, DrawFromProductsEvent(
                campaign, campaign_product), prize_campaign_product, qty,
        )
        response_json = get_winner_json(lucky_draw.winner_list)

        return Response(response_json, status=status.HTTP_200_OK)
