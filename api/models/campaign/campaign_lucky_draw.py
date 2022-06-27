from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class CampaignLuckyDraw(models.Model):
    class Meta:
        db_table = 'api_campaign_lucky_draw'

    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.CASCADE, related_name='campaign_lucky_draws')
    campaign_product = models.ForeignKey(
        CampaignProduct, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaign_lucky_draws')


    num_of_winner = models.IntegerField(null=True, blank=True, default=1)
    winner_list = models.JSONField(default=list, null=True, blank=True)

    type = models.CharField(max_length=255, null=True, blank=True)    #'like, perchase, product, keyword'
    status = models.CharField(max_length=255, null=True, blank=True)    #'initiate, finish'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=dict, null=True, blank=True)

    repeatable = models.BooleanField(default=True ,null=False, blank=False)
    animation = models.CharField(max_length=255, null=True, blank=True)
    spin_time = models.IntegerField(null=False, blank=False, default=2)
    comment = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True, default='')
    
class CampaignLuckyDrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignLuckyDraw
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)


class CampaignLuckyDrawAdmin(admin.ModelAdmin):
    model = CampaignLuckyDraw
    list_display = [field.name for field in CampaignLuckyDraw._meta.fields]
    search_fields = [field.name for field in CampaignLuckyDraw._meta.fields]
