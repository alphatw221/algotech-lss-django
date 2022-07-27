from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct

from djongo import models
from rest_framework import serializers


class CampaignQuizGame(models.Model):
    class Meta:
        db_table = 'api_campaign_quiz_game'
    
    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.CASCADE, related_name='campaign_quiz_game')
    
    prize = models.ForeignKey(
        CampaignProduct, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaign_quiz_game_prize')
    
    title = models.CharField(max_length=255, null=True, blank=True, default='')
    question = models.CharField(max_length=255, null=True, blank=True, default='')
    answer = models.CharField(max_length=255, null=True, blank=True, default='')
    remark = models.CharField(max_length=255, null=True, blank=True, default='')
    num_of_winner = models.IntegerField(null=True, blank=True, default=1)
    repeatable = models.BooleanField(default=True ,null=False, blank=False)
    follower = models.BooleanField(default=True ,null=False, blank=False)

    winner_list = models.JSONField(default=list, null=True, blank=True)
    meta = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    