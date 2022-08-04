from functools import partial
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from api import models
import lib
import json
import datetime

class CampaignQuizGameViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.campaign.campaign_quiz_game.CampaignQuizGame.objects.all().order_by('id')


    @action(detail=False, methods=['POST'], url_path=r'(?P<campaign_id>[^/.]+)/create', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_quiz_game(self, request, campaign_id):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        prize = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, int(request.data.get('prize', {}).get('id', 0)))
        question_list = request.data.get('quiz_games', [])

        for question in question_list:
            if question['question'] in ['', None]:
                return Response({'message': 'question null'}, status=status.HTTP_400_BAD_REQUEST)
            elif question['answer'] in ['', None]:
                return Response({'message': 'answer null'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = models.campaign.campaign_quiz_game_bundle.CampaignQuizGameBundleSerializerCreate(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        quiz_game_bundle = serializer.save()
        quiz_game_bundle.campaign = campaign
        quiz_game_bundle.prize = prize
        quiz_game_bundle.save()

        for question in question_list:
            serializer = models.campaign.campaign_quiz_game.CampaignQuizGameSerializerCreate(data = {'question': question['question'], 'answer': question['answer']})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            quiz_game = serializer.save()
            quiz_game.quiz_game_bundle = quiz_game_bundle
            quiz_game.save()

        return Response(models.campaign.campaign_quiz_game_bundle.CampaignQuizGameBundleSerializer(quiz_game_bundle).data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['PUT'], url_path=r'update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_quiz_game(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        quiz_game_bundle = lib.util.verify.Verify.get_quiz_game_bundle(pk)
        campaign = quiz_game_bundle.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)
        prize = lib.util.verify.Verify.get_campaign_product_from_campaign(campaign, int(request.data.get('prize', {}).get('id', 0)))
        question_list = request.data.get('quiz_games', [])

        for question in question_list:
            if question['question'] in ['', None]:
                return Response({'message': 'question null'}, status=status.HTTP_400_BAD_REQUEST)
            elif question['answer'] in ['', None]:
                return Response({'message': 'answer null'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = models.campaign.campaign_quiz_game_bundle.CampaignQuizGameBundleSerializerUpdate(quiz_game_bundle, data = request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        quiz_game_bundle = serializer.save()
        quiz_game_bundle.prize = prize
        quiz_game_bundle.save()

        ## remove old quiz game then add new one
        quiz_games = models.campaign.campaign_quiz_game.CampaignQuizGameBundleSerializerWithEachQuiz(quiz_game_bundle).data.get('quiz_games')
        for quiz_game in quiz_games:
            for key, val in quiz_game.items():
                if (key == 'id'):
                    models.campaign.campaign_quiz_game.CampaignQuizGame.objects.get(id=val).delete()

        for question in question_list:
            serializer = models.campaign.campaign_quiz_game.CampaignQuizGameSerializerCreate(data = {'question': question['question'], 'answer': question['answer']})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            quiz_game = serializer.save()
            quiz_game.quiz_game_bundle = quiz_game_bundle
            quiz_game.save()

        return Response(models.campaign.campaign_quiz_game_bundle.CampaignQuizGameBundleSerializer(quiz_game_bundle).data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_quiz_game(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        quiz_game_bundle = lib.util.verify.Verify.get_quiz_game_bundle(pk)
        campaign = quiz_game_bundle.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)
        
        quiz_game_bundle.delete()

        return Response({'message': 'delete success'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_quiz_game(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        quiz_game_bundle = lib.util.verify.Verify.get_quiz_game_bundle(pk)

        campaign = quiz_game_bundle.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        return Response(models.campaign.campaign_quiz_game.CampaignQuizGameBundleSerializerWithEachQuiz(quiz_game_bundle).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/list', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_quiz_game(self, request, campaign_id):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        return Response(models.campaign.campaign_quiz_game.CampaignQuizGameBundleSerializerWithEachQuiz(campaign.quiz_game_bundle.all(), many=True).data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['GET'], url_path=r'start', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def start_quiz_game(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        quiz_game = lib.util.verify.Verify.get_quiz_game(pk)

        quiz_game.start_at = datetime.datetime.now()
        quiz_game.save()

        campaign = quiz_game.quiz_game_bundle.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        return Response(models.campaign.campaign_quiz_game.CampaignQuizGameSerializer(quiz_game).data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['GET'], url_path=r'stop', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def stop_quiz_game(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        quiz_game = lib.util.verify.Verify.get_quiz_game(pk)

        quiz_game.end_at = datetime.datetime.now()
        quiz_game.save()

        campaign = quiz_game.quiz_game_bundle.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        # winner_list = lib.helper.quiz_game_helper.quiz(campaign, quiz_game)

        return Response(models.campaign.campaign_quiz_game.CampaignQuizGameSerializer(quiz_game).data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['POST'], url_path=r'result', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def result_quiz_game(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        quiz_game_bundle = lib.util.verify.Verify.get_quiz_game_bundle(pk)

        campaign = quiz_game_bundle.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        winner_list = lib.helper.quiz_game_helper.quiz(campaign, quiz_game_bundle)

        return Response(winner_list, status=status.HTTP_200_OK)