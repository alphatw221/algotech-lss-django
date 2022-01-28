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
from backend.pymongo.mongodb import db, client
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

def verify_request(api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id, campaign_product_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)
    prize_campaign_product = Verify.get_campaign_product_from_campaign(
        campaign, prize_campaign_product_id)

    if campaign_product_id:
        campaign_product_id = Verify.get_campaign_product_from_campaign(
            campaign, campaign_product_id)
        return platform, campaign, prize_campaign_product, campaign_product_id

    return platform, campaign, prize_campaign_product


def verify_user(api_user, platform_name, platform_id):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    if platform:
        return True


def get_winner_json(winner_lists):
    response_list = []
    try:
        if (len(winner_lists[0]) == 3):
            for winner_list in winner_lists:
                winner = {}
                winner['platform'] = winner_list[0]
                winner['customer_id'] = winner_list[1]
                winner['customer_name'] = winner_list[2]
                
                if winner_list[0] == 'facebook':
                    try:
                        winner_datas = db.api_user.find({'facebook_info.id': winner_list[1]})
                        for winner_data in winner_datas:
                            winner['img_url'] = winner_data['facebook_info']['picture']
                    except:
                        winner['img_url'] = ''

                response_list.append(winner)
            response_json = { 'winner_list': response_list }
        # elif (len(winner_lists[0]) > 5):
        #     for winner in winner_lists:
        #         # print ('winner')
        #         # print (winner)
        #         winnerJson = {}
        #         winner_info = db.api_user.find_one({'facebook_info.id': winner})
        #         winnerJson['platform'] = 'facebook'
        #         winnerJson['customer_id'] = winner
        #         winnerJson['customer_name'] = winner_info['name']
        #         winnerJson['customer_id'] = winner_info['picture']
        #         response_list.append(winnerJson)
        #     response_json = { 'winner_list': response_list }
        else:
            response_json = { 'winner_list': [] }
    except:
        response_json = { 'winner_list': [] }
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
        api_user, platform_id, platform_name = getparams(
            request, ("platform_id", "platform_name")
        )
        campaign_id = int(request.query_params.get('campaign_id'))
        _verify_user = verify_user(api_user, platform_name, platform_id)

        winner_json = {}
        if _verify_user:
            winner_json['campaign_title'] = db.api_campaign.find_one({'id': campaign_id})['title']

            winner_infos = db.api_campaign_lucky_draw.find({'campaign_id': campaign_id})
            winner_list = []
            for winner_info in winner_infos:
                if winner_info['winner_list']:
                    response = get_winner_json(winner_info['winner_list'])
                    for winner in response['winner_list']:
                        json = {}
                        prize_name = db.api_campaign_product.find_one({'id': winner_info['prize_campaign_product_id']})['name']

                        json['name'] = winner['customer_name']
                        json['img'] = winner['img_url']
                        json['prize_name'] = prize_name
                        json['datetime'] = winner_info['created_at']
                        winner_list.append(json)
                    print (winner_info['id'])
            winner_json['winner_list'] = winner_list

        return Response(winner_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'likes')
    @api_error_handler
    def lucky_draw_likes(self, request):
        api_user, platform_id, platform_name, campaign_id, prize_campaign_product_id, qty, unrepeat = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "prize_campaign_product_id", "qty", "unrepeat")
        )
        qty = int(qty)
        api_user = request.user.api_users.get(type='user')

        _, campaign, prize_campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id)

        lucky_draw = CampaignLuckyDrawManager.process(
            campaign, DrawFromCampaignLikesEvent(
                campaign, unrepeat, qty), prize_campaign_product, qty,
        )
        response_json = get_winner_json(lucky_draw.winner_list)

        return Response(response_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'comment')
    @api_error_handler
    def lucky_draw_comment(self, request):
        api_user, platform_id, platform_name, campaign_id, prize_campaign_product_id, keyword, qty, unrepeat = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "prize_campaign_product_id", "keyword", "qty", "unrepeat")
        )
        qty = int(qty)
        api_user = request.user.api_users.get(type='user')

        _, campaign, prize_campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id)

        lucky_draw = CampaignLuckyDrawManager.process(
            campaign, DrawFromCampaignCommentsEvent(
                campaign, keyword, unrepeat, qty), prize_campaign_product, qty,
        )
        response_json = get_winner_json(lucky_draw.winner_list)

        return Response(response_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'carts')
    @api_error_handler
    def lucky_draw_cart(self, request):
        api_user, platform_id, platform_name, campaign_id, prize_campaign_product_id, campaign_product_id, qty, unrepeat = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "prize_campaign_product_id", "campaign_product_id", "qty", "unrepeat")
        )
        qty = int(qty)
        api_user = request.user.api_users.get(type='user')

        _, campaign, prize_campaign_product, campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id, campaign_product_id = campaign_product_id)

        lucky_draw = CampaignLuckyDrawManager.process(
            campaign, DrawFromCartProductsEvent(
                campaign, campaign_product, unrepeat, qty), prize_campaign_product, qty,
        )
        response_json = get_winner_json(lucky_draw.winner_list)

        return Response(response_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'products')
    @api_error_handler
    def lucky_draw_products(self, request):
        api_user, platform_id, platform_name, campaign_id, prize_campaign_product_id, campaign_product_id, qty, unrepeat = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "prize_campaign_product_id", "campaign_product_id", "qty", "unrepeat")
        )
        qty = int(qty)
        api_user = request.user.api_users.get(type='user')

        _, campaign, prize_campaign_product, campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id, campaign_product_id = campaign_product_id)

        lucky_draw = CampaignLuckyDrawManager.process(
            campaign, DrawFromProductsEvent(
                campaign, campaign_product, unrepeat, qty), prize_campaign_product, qty,
        )
        response_json = get_winner_json(lucky_draw.winner_list)

        return Response(response_json, status=status.HTTP_200_OK)
