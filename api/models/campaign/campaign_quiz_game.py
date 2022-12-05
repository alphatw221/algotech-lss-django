from email.policy import default
from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer
from api.models.campaign.campaign_quiz_game_bundle import CampaignQuizGameBundle, CampaignQuizGameBundleSerializer

from djongo import models
from rest_framework import serializers

STATUS_INIT='initiate'
STATUS_FINISH='finish'

class CampaignQuizGame(models.Model):
    class Meta:
        db_table = 'api_campaign_quiz_game'
    
    quiz_game_bundle = models.ForeignKey(
        CampaignQuizGameBundle, blank=True, null=True, on_delete=models.CASCADE, related_name='quiz_games') 
    
    title = models.CharField(max_length=255, null=True, blank=True, default='')
    question = models.CharField(max_length=255, null=True, blank=True, default='')
    answer = models.CharField(max_length=255, null=True, blank=True, default='')
    remark = models.CharField(max_length=255, null=True, blank=True, default='')

    meta = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True) 

    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CampaignQuizGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignQuizGame
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    meta = serializers.JSONField(default=dict)

class CampaignQuizGameSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = CampaignQuizGame
        fields = ['title', 'question', 'answer', 'meta']
        read_only_fields = ['created_at', 'updated_at']
    
    meta = serializers.JSONField(default=dict)

class CampaignQuizGameSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = CampaignQuizGame
        fields = ['title', 'question', 'answer', 'meta']
        read_only_fields = ['created_at', 'updated_at']
    
    meta = serializers.JSONField(default=dict)


class CampaignQuizGameBundleSerializerWithEachQuiz(CampaignQuizGameBundleSerializer):

    quiz_games = CampaignQuizGameSerializer(read_only=True, many=True)
