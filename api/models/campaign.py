from django.contrib import admin
from djongo import models
from rest_framework import serializers
from ..models.user import User


class Campaign(models.Model):

    def __str__(self):
        return str(self.id)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='campaigns')

    campaign_id = models.CharField(max_length=255, null=True, blank=True)
    post_id = models.CharField(max_length=255, null=True, blank=True)
    live_video_id = models.CharField(max_length=255, null=True, blank=True)
    embed_url = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    user_id_added = models.CharField(max_length=255, null=True, blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    platform_meta = models.JSONField(default=None, null=True, blank=True)
    meta = models.JSONField(default=None, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = '__all__'

    platform_meta = serializers.JSONField()
    meta = serializers.JSONField()


class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    list_display = [field.name for field in Campaign._meta.fields]
    search_fields = [field.name for field in Campaign._meta.fields]
