from itsdangerous import Serializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
from lib.helper import lucky_draw
class CampaignLuckyDrawViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.campaign.campaign_lucky_draw.CampaignLuckyDraw.objects.all().order_by('id')

    # @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/winners', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def list_winner(self, request, campaign_id):

    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

    #     return Response([], status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_campaign_lucky_draw(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign)

        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(lucky_draw).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_lucky_draw(self, request, campaign_id):

        campaign_product_id, type= \
            lib.util.getter.getdata(request, ("campaign_product_id", "type"), required=True)

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)

        if type not in models.campaign.campaign_lucky_draw.TYPE_CHOICES:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid lucky_draw type')

        serializer = models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializerCreate(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        lucky_draw = serializer.save()
        
        lucky_draw.campaign =campaign
        lucky_draw.campaign_product =campaign_product
        lucky_draw.type = type
        lucky_draw.status = models.campaign.campaign_lucky_draw.STATUS_INIT
        lucky_draw.save()
        
        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(lucky_draw).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['PUT'], url_path=r'update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_lucky_draw(self, request, pk):

        campaign_product_id, type= \
            lib.util.getter.getdata(request, ("campaign_product_id", "type"), required=True)

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)

        if type not in models.campaign.campaign_lucky_draw.TYPE_CHOICES:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid lucky_draw type')

        serializer = models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializerUpdate(lucky_draw, data = request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        lucky_draw = serializer.save()
        
        lucky_draw.campaign_product =campaign_product
        lucky_draw.type = type
        lucky_draw.save()
        
        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(lucky_draw).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['DELETE'], url_path=r'/delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_lucky_draw(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign)

        if lucky_draw.status==models.campaign.campaign_lucky_draw.STATUS_FINISH:
            raise lib.error_handle.error.api_error.ApiVerifyError('lucky draw has already finished')

        lucky_draw.delete()
        
        return Response('delete success', status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_campaign_lucky_draw(self, request, campaign_id):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(campaign.campaign_lucky_draws.all(), many=True).data, status=status.HTTP_200_OK)



    @action(detail=True, methods=['POST'], url_path=r'draw', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def draw_campaign_lucky_draw(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lucky_draw = lib.util.verify.Verify.get_lucky_draw(pk)
        campaign = lucky_draw.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign)

        winner_list = lib.helper.lucky_draw.draw(campaign, lucky_draw)
        return Response(models.campaign.campaign_lucky_draw.CampaignLuckyDrawSerializer(lucky_draw).data, status=status.HTTP_200_OK)




    # @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/likes', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def lucky_draw_likes(self, request, campaign_id):

    #     campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
    #     campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
    #     winner_list = lib.helper.lucky_draw.draw_likes(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
    #     return Response(winner_list, status=status.HTTP_200_OK)


    # @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/keyword', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def lucky_draw_keyword(self, request, campaign_id):

    #     campaign_product_id, num_of_winner, repeatable, keyword = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable", "keyword"), required=True)
    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
    #     campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
    #     winner_list = lib.helper.lucky_draw.draw_keyword(campaign, keyword, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
    #     return Response(winner_list, status=status.HTTP_200_OK)


    # @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/perchase', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def lucky_draw_perchase(self, request, campaign_id):

    #     campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
    #     campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
    #     winner_list = lib.helper.lucky_draw.draw_perchase(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
    #     return Response(winner_list, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/product', permission_classes=(IsAuthenticated,))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def lucky_draw_product(self, request, campaign_id):

    #     campaign_product_id, num_of_winner, repeatable = lib.util.getter.getdata(request, ("campaign_product_id", "num_of_winner", "repeatable"), required=True)
    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
    #     campaign_product = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, campaign_product_id)
    #     winner_list = lib.helper.lucky_draw.draw_product(campaign, campaign_product, num_of_winner, limit=100, repeatable=repeatable)
    
    #     return Response(winner_list, status=status.HTTP_200_OK)