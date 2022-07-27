from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib, json

class CampaignQuizGameViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.campaign.campaign_quiz_game.CampaignQuizGame.objects.all().order_by('id')


    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/create', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_quiz_game(self, request, campaign_id):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        data, = lib.util.getter.getdata(request, ('data', ), required=True)
        data = json.load(data)
        prize = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, int(data.get('prize', {}).get('id', 0)))

        serializer = models.campaign.campaign_quiz_game.CampaignQuizGameSerializerCreate(data = data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        quiz_game = serializer.save()

        quiz_game.campaign = campaign
        quiz_game.prize = prize
        quiz_game.status = models.campaign.campaign_quiz_game.STATUS_INIT
        quiz_game.save()

        return Response('poop', status=status.HTTP_200_OK)
