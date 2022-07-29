from email.policy import default
from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer

from djongo import models
from rest_framework import serializers

STATUS_INIT='initiate'
STATUS_FINISH='finish'

class CampaignQuizGame(models.Model):
    class Meta:
        db_table = 'api_campaign_quiz_game'
    
    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.CASCADE, related_name='quiz_games')
    
    prize = models.ForeignKey(
        CampaignProduct, blank=True, null=True, on_delete=models.SET_NULL, related_name='quiz_games')
    
    title = models.CharField(max_length=255, null=True, blank=True, default='')
    question = models.CharField(max_length=255, null=True, blank=True, default='')
    answer = models.CharField(max_length=255, null=True, blank=True, default='')
    remark = models.CharField(max_length=255, null=True, blank=True, default='')
    num_of_winner = models.IntegerField(null=True, blank=True, default=1)
    repeatable = models.BooleanField(default=True ,null=False, blank=False)
    is_follower = models.BooleanField(default=True ,null=False, blank=False)

    winner_list = models.JSONField(default=list, null=True, blank=True)
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

    prize = CampaignProductSerializer(read_only=True, default=dict)
    meta = serializers.JSONField(default=dict)

class CampaignQuizGameSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = CampaignQuizGame
        fields = ['title', 'question', 'answer', 'remark', 'num_of_winner', 'repeatable', 'is_follower', 'meta']
        read_only_fields = ['created_at', 'updated_at']
    
    meta = serializers.JSONField(default=dict)