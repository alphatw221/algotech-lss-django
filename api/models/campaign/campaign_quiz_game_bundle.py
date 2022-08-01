from email.policy import default
from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer

from djongo import models
from rest_framework import serializers

STATUS_INIT='initiate'
STATUS_FINISH='finish'

class CampaignQuizGameBundle(models.Model):
    class Meta:
        db_table = 'api_campaign_quiz_game_bundle'
    
    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.CASCADE, related_name='quiz_game_bundle')
    
    prize = models.ForeignKey(
        CampaignProduct, blank=True, null=True, on_delete=models.SET_NULL, related_name='quiz_game_bundle')
    
    remark = models.CharField(max_length=255, null=True, blank=True, default='')
    num_of_winner = models.IntegerField(null=True, blank=True, default=1)
    repeatable = models.BooleanField(default=True ,null=False, blank=False)
    is_follower = models.BooleanField(default=True ,null=False, blank=False)

    winner_list = models.JSONField(default=list, null=True, blank=True)
    meta = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)