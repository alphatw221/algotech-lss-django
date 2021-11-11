from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.campaign.campaign import Campaign


class CampaignOrder(models.Model):
    class Meta:
        db_table = 'api_campaign_order'

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='campaign_orders')

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(default=None, null=True, blank=True)
    image = models.CharField(max_length=512, null=True, blank=True)

    platform = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.id)


class CampaignOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignOrder
        fields = '__all__'

    meta = serializers.JSONField(default=dict)


class CampaignOrderAdmin(admin.ModelAdmin):
    model = CampaignOrder
    list_display = [field.name for field in CampaignOrder._meta.fields]
    search_fields = [field.name for field in CampaignOrder._meta.fields]
