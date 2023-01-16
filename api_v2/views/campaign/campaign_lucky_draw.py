from django.conf import settings
from django.core.files.base import ContentFile
from automation import jobs
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser


from api import models
from api_v2 import rule
import lib, json
import service

class CampaignLuckyDrawViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.campaign.campaign_lucky_draw.CampaignLuckyDraw.objects.all().order_by('id')

    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/winners', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_winner(self, request, campaign_id):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        winner_list = campaign.meta.get('winner_list', [])

        return Response(winner_list, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_campaign_lucky_draw(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(lucky_draw).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_lucky_draw(self, request, campaign_id):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        data = request.data

        data['campaign'] = campaign.id
        prize = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, data.get('prize_id'))
        data['prize'] = prize.id

        if data.get('type') == models.campaign.campaign_lucky_draw.TYPE_PRODUCT:
            campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, data.get('campaign_product_id'))
            data['campaign_product'] = campaign_product.id
        else:
            data['campaign_product'] = None

        print(data)
        serializer = models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializerCreate(data = data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        lucky_draw = serializer.save()

        
        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(lucky_draw).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['PUT'], url_path=r'update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_lucky_draw(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        data = request.data
        if data.get('prize_id'):
            prize = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, data.get('prize_id'))
            data['prize'] = prize.id

        if data.get('type') == models.campaign.campaign_lucky_draw.TYPE_PRODUCT:
            campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, data.get('campaign_product_id'))
            data['campaign_product'] = campaign_product.id
        else:
            data['campaign_product'] = None
            
        serializer = models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializerUpdate(lucky_draw, data = data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        lucky_draw = serializer.save()

        
        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(lucky_draw).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_lucky_draw(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        if lucky_draw.status==models.campaign.campaign_lucky_draw.STATUS_FINISH:
            raise lib.error_handle.error.api_error.ApiVerifyError('lucky_draw_has_already_finished')

        lucky_draw.delete()
        
        return Response('delete success', status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_campaign_lucky_draw(self, request, campaign_id):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(campaign.lucky_draws.all(), many=True).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['POST'], url_path=r'draw', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def draw_campaign_lucky_draw(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        winner_list = lib.helper.lucky_draw_helper.draw(campaign, lucky_draw, api_user)
        return Response(winner_list, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'draw/check', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_draw_valid(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)
        
        ret = rule.rule_checker.lucky_draw_rule_checker.LuckyDrawStartRuleChecker.check(
            check_list=[
            rule.check_rule.lucky_draw_check_rule.LuckyDrawCheckRule.is_draw_type_valid,
            rule.check_rule.lucky_draw_check_rule.LuckyDrawCheckRule.is_draw_prize_valid,
            rule.check_rule.lucky_draw_check_rule.LuckyDrawCheckRule.is_connected_to_any_platform,
        ],**{
            'lucky_draw': lucky_draw, 'campaign': campaign
        })

        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(lucky_draw).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'list/animation', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_campaign_lucky_draw_animation(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        static_assets = user_subscription.assets.filter(type=models.user.static_assets.TYPE_ANIMATION)
        
        return Response(models.user.static_assets.StaticAssetsSerializer(static_assets, many=True).data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/likes', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def lucky_draw_likes(self, request, campaign_id):

    #     campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
    #     campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
    #     winner_list = lib.helper.lucky_draw_helper.draw_likes(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
    #     return Response(winner_list, status=status.HTTP_200_OK)


    # @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/keyword', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def lucky_draw_keyword(self, request, campaign_id):

    #     campaign_product_id, num_of_winner, repeatable, keyword = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable", "keyword"), required=True)
    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
    #     campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
    #     winner_list = lib.helper.lucky_draw_helper.draw_keyword(campaign, keyword, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
    #     return Response(winner_list, status=status.HTTP_200_OK)


    # @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/perchase', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def lucky_draw_perchase(self, request, campaign_id):

    #     campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
    #     campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
    #     winner_list = lib.helper.lucky_draw_helper.draw_perchase(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
    #     return Response(winner_list, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/product', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def lucky_draw_product(self, request, campaign_id):

    #     campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
    #     campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
    #     winner_list = lib.helper.lucky_draw_helper.draw_product(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
    #     return Response(winner_list, status=status.HTTP_200_OK)