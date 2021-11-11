from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.user.user import User
from api.models.facebook.facebook_page import FacebookPage, FacebookPageSerializer
from api.models.youtube.youtube_channel import YoutubeChannel, YoutubeChannelSerializer
from dataclasses import dataclass


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
    youtube_channel = models.ForeignKey(
        YoutubeChannel, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    meta = models.JSONField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.id)


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

    meta = serializers.JSONField(default=dict)
    # facebook_page = FacebookPageSerializer()
    # youtube_channel = YoutubeChannelSerializer()


class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    list_display = [field.name for field in Campaign._meta.fields]
    search_fields = [field.name for field in Campaign._meta.fields]


@dataclass
class FacebookCampaign:
    page_id: str = ''
    post_id: str = ''
    live_video_id: str = ''
    embed_url: str = ''
