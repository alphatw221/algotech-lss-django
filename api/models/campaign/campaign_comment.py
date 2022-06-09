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
    platform=models.CharField(max_length=255, null=True, blank=True)
    campaign=models.ForeignKey(
        Campaign, null=True, on_delete=models.SET_NULL, related_name='comments')
    message=models.CharField(max_length=255, null=True, blank=True)
    created_time=models.FloatField(null=True, blank=True, default=0)
    customer_id=models.CharField(max_length=255, null=True, blank=True)
    customer_name=models.CharField(max_length=255, null=True, blank=True)
    image=models.CharField(max_length=255, null=True, blank=True)
    categories=models.JSONField(default=list, null=True, blank=True)
    main_categories=models.JSONField(default=list, null=True, blank=True)



class CampaignCommentSerializerTest(serializers.ModelSerializer):
    class Meta:
        model = CampaignComment
        exclude=['id', 'created_time']


class CampaignCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignComment
        exclude=['id']
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)
    categories = serializers.JSONField(default=list, required=False)
    main_categories = serializers.JSONField(default=list, required=False)
    created_time = serializers.CharField(default=None, required=False)


class CampaignCommentAdmin(admin.ModelAdmin):
    model = CampaignComment
    list_display = [field.name for field in CampaignComment._meta.fields]
    search_fields = [field.name for field in CampaignComment._meta.fields]

api_campaign_comment_template={f.get_attname():f.get_default() if f.has_default() else None for f in CampaignComment._meta.fields}