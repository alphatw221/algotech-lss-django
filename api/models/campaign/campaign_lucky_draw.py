
#TODO: WIP
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct


class CampaignLuckyDraw(models.Model):
    class Meta:
        db_table = 'api_lucky_draw'

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='campaign_lucky_draws')
    campaign_product = models.ForeignKey(
        CampaignProduct, on_delete=models.CASCADE, related_name='campaign_lucky_draws')
    source_type = models.CharField(max_length=255, null=True, blank=True)
    source_id = models.IntegerField(null=True, blank=True, default=None)

    keyword = models.CharField(max_length=255, null=True, blank=True)
    num_of_winner = models.IntegerField(null=True, blank=True, default=1)
    candidate_set = models.JSONField(default=None, null=True, blank=True)
    winner_list = models.JSONField(default=None, null=True, blank=True)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.id)


class CampaignLuckyDrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignLuckyDraw
        fields = '__all__'

    meta = serializers.JSONField(default=dict)


class CampaignLuckyDrawAdmin(admin.ModelAdmin):
    model = CampaignLuckyDraw
    list_display = [field.name for field in CampaignLuckyDraw._meta.fields]
    search_fields = [field.name for field in CampaignLuckyDraw._meta.fields]
