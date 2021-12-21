from api.models.campaign.campaign_lucky_draw import (
    CampaignLuckyDraw, CampaignLuckyDrawSerializer)
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError

from rest_framework.decorators import action
from rest_framework.response import Response

from backend.campaign.campaign_lucky_draw.manager import CampaignLuckyDrawManager
from backend.campaign.campaign_lucky_draw.event import DrawFromCampaignLikesEvent, DrawFromCampaignCommentsEvent, DrawFromCartProductsEvent

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_lucky_draw import CampaignLuckyDraw


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
    def list_winner(self, request):
        try:
            campaign_id = request.query_params.get('campaign_id')
            winner_list = CampaignLuckyDraw.objects.filter(campaign_id=campaign_id)

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"message": "error occerd during draw"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(winner_list, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'likes')
    def lucky_draw_likes(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            prize_campaign_product_id = request.query_params.get(
                'prize_campaign_product_id')
            api_user = request.user.api_users.get(type='user')
            qty = request.user.api_users.get(
                type='qty') if request.user.api_users.get(type='qty') else 1

            _, campaign, prize_campaign_product = verify_request(
                api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id)

            lucky_draw = CampaignLuckyDrawManager.process(
                campaign, DrawFromCampaignLikesEvent(
                    campaign), prize_campaign_product, qty,
            )

            response_json = {
                'draw_result': lucky_draw.meta['announcement_history']['response_result'],
                'winner_list': lucky_draw.winner_list
            }

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"message": "error occerd during draw"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'comment')
    def lucky_draw_comment(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            prize_campaign_product_id = request.query_params.get(
                'prize_campaign_product_id')
            api_user = request.user.api_users.get(type='user')
            qty = request.user.api_users.get(
                type='qty') if request.user.api_users.get(type='qty') else 1

            _, campaign, prize_campaign_product = verify_request(
                api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id)

            lucky_draw = CampaignLuckyDrawManager.process(
                campaign, DrawFromCampaignCommentsEvent(
                    campaign, 'order'), prize_campaign_product, qty,
            )

            response_json = {
                'draw_result': lucky_draw.meta['announcement_history']['response_result'],
                'winner_list': lucky_draw.winner_list
            }

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"message": "error occerd during draw"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response_json, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'cart')
    def lucky_draw_cart(self, request):
        try:
            platform_id = request.query_params.get('platform_id')
            platform_name = request.query_params.get('platform_name')
            campaign_id = request.query_params.get('campaign_id')
            campaign_product_id = request.query_params.get(
                'campaign_product_id')
            prize_campaign_product_id = request.query_params.get(
                'prize_campaign_product_id')
            api_user = request.user.api_users.get(type='user')
            qty = request.user.api_users.get(
                type='qty') if request.user.api_users.get(type='qty') else 1

            _, campaign, prize_campaign_product, campaign_product = verify_request(
                api_user, platform_name, platform_id, campaign_id, prize_campaign_product_id, campaign_product_id = campaign_product_id)

            lucky_draw = CampaignLuckyDrawManager.process(
                campaign, DrawFromCartProductsEvent(
                    campaign, campaign_product), prize_campaign_product, qty,
            )

            response_json = {
                'draw_result': lucky_draw.meta['announcement_history']['response_result'],
                'winner_list': lucky_draw.winner_list
            }

        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"message": "error occerd during draw"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response_json, status=status.HTTP_200_OK)
