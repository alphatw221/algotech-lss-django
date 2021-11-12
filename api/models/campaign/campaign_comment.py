from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.campaign.campaign import Campaign


class CampaignComment(models.Model):
    class Meta:
        db_table = 'api_campaign_comment'

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='comments')

    comment_id = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True, default=None)
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=512, null=True, blank=True)

    platform = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=None)

    def __str__(self):
        return self.message


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
