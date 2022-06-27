from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
class CampaignLuckyDrawViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.campaign.campaign_lucky_draw.CampaignLuckyDraw.objects.all().order_by('id')

    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/winners', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_winner(self, request, campaign_id):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        return Response([], status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/likes', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def lucky_draw_likes(self, request, campaign_id):

        campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
        winner_list = lib.helper.lucky_draw.draw_likes(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
        return Response(winner_list, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/keyword', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def lucky_draw_keyword(self, request, campaign_id):

        campaign_product_id, num_of_winner, repeatable, keyword = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable", "keyword"), required=True)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
        winner_list = lib.helper.lucky_draw.draw_keyword(campaign, keyword, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
        return Response(winner_list, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/perchase', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def lucky_draw_perchase(self, request, campaign_id):

        campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
        winner_list = lib.helper.lucky_draw.draw_perchase(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
        return Response(winner_list, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/product', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def lucky_draw_product(self, request, campaign_id):

        campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
        winner_list = lib.helper.lucky_draw.draw_product(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
        return Response(winner_list, status=status.HTTP_200_OK)