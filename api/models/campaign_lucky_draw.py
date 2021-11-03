from django.contrib import admin
from djongo import models
from rest_framework import serializers
from ..models.campaign import Campaign
from ..models.campaign_product import CampaignProduct


class CampaignLuckyDraw(models.Model):

    def __str__(self):
        return str(self.id)

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='campaign_lucky_draws')

    campaign_product = models.ForeignKey(
        CampaignProduct, on_delete=models.CASCADE, related_name='campaign_lucky_draws')

    order_code = models.CharField(max_length=255, null=True, blank=True)
    num_of_winner = models.CharField(max_length=255, null=True, blank=True)
    candidate_set = models.TextField(default=None, null=True, blank=True)
    winner_list = models.TextField(default=None, null=True, blank=True)

    platform_meta = models.JSONField(default=None, null=True, blank=True)
    meta = models.JSONField(default=None, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CampaignLuckyDrawSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignLuckyDraw
        fields = '__all__'

    platform_meta = serializers.JSONField()
    meta = serializers.JSONField()


class CampaignLuckyDrawAdmin(admin.ModelAdmin):
    model = CampaignLuckyDraw
    list_display = [field.name for field in CampaignLuckyDraw._meta.fields]
    search_fields = [field.name for field in CampaignLuckyDraw._meta.fields]
