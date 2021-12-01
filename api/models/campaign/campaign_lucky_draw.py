from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class CampaignLuckyDraw(models.Model):
    class Meta:
        db_table = 'api_lucky_draw'

    SOURCE_TYPE_CHOICES = [
        ('n/a', 'Not available'),
        ('cart_product', 'Cart Product'),
        ('campaign_comment', 'Campaign Comment'),
        ('campaign_likes', 'Campaign Likes'),
    ]

    CONDITION_TYPE_CHOICES = [
        ('n/a', 'Not available'),
        ('cart_product', 'Draw from Cart Products'),
        ('campaign_comment', 'Draw from Campaign Comments'),
        ('campaign_likes', 'Draw from Campaign Likes'),

    ]

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='campaign_lucky_draws')
    prize_campaign_product = models.ForeignKey(
        CampaignProduct, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaign_lucky_draws')

    source_id = models.IntegerField(null=True, blank=True, default=None)
    source_type = models.CharField(max_length=255, blank=True,
                                   choices=SOURCE_TYPE_CHOICES, default='n/a')
    condition = models.CharField(max_length=255, null=True, blank=True)
    condition_type = models.CharField(max_length=255, blank=True,
                                      choices=CONDITION_TYPE_CHOICES, default='n/a')
    num_of_winner = models.IntegerField(null=True, blank=True, default=1)
    candidate_list = models.JSONField(default=list, null=True, blank=True)
    winner_list = models.JSONField(default=list, null=True, blank=True)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=dict, null=True, blank=True)


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
