from django.contrib import admin
from djongo import models
from rest_framework import serializers
from ..models.campaign import Campaign


class CampaignComment(models.Model):

    def __str__(self):
        return str(self.id)

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='comments')

    comment_id = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    picture_url = models.CharField(max_length=255, null=True, blank=True)

    platform_meta = models.JSONField(default=None, null=True, blank=True)
    meta = models.JSONField(default=None, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CampaignCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignComment
        fields = '__all__'

    platform_meta = serializers.JSONField()
    meta = serializers.JSONField()


class CampaignCommentAdmin(admin.ModelAdmin):
    model = CampaignComment
    list_display = [field.name for field in CampaignComment._meta.fields]
    search_fields = [field.name for field in CampaignComment._meta.fields]
