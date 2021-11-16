from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.user.user import User
from api.models.facebook.facebook_page import FacebookPage, FacebookPageSerializer
from api.models.youtube.youtube_channel import YoutubeChannel, YoutubeChannelSerializer
from api.models.campaign.facebook_campaign import FacebookCampaign


class Campaign(models.Model):
    class Meta:
        db_table = 'api_campaign'

    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='campaigns')

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    facebook_page = models.ForeignKey(
        FacebookPage, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    facebook_campaign = models.JSONField(null=True, blank=True, default=dict)
    youtube_channel = models.ForeignKey(
        YoutubeChannel, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    youtube_campaign = models.JSONField(null=True, blank=True, default=dict)
    meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.title


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)
    # facebook_page = FacebookPageSerializer()
    facebook_campaign = serializers.JSONField(default=dict)
    # youtube_channel = YoutubeChannelSerializer()
    youtube_campaign = serializers.JSONField(default=dict)


class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    list_display = [field.name for field in Campaign._meta.fields]
    search_fields = [field.name for field in Campaign._meta.fields]