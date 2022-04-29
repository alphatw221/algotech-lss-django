import time

from api.models.campaign.campaign import Campaign
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class CampaignComment(models.Model):
    class Meta:
        db_table = 'api_campaign_comment'

    id = models.IntegerField(primary_key=True, unique=False)  

class CampaignCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignComment
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)


class CampaignCommentAdmin(admin.ModelAdmin):
    model = CampaignComment
    list_display = [field.name for field in CampaignComment._meta.fields]
    search_fields = [field.name for field in CampaignComment._meta.fields]
