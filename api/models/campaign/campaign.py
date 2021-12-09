from api.models.facebook.facebook_page import (FacebookPage,
                                               FacebookPageInfoSerializer, FacebookPageSerializer)

from api.models.instagram.instagram_profile import (
    InstagramProfile, InstagramProfileInfoSerializer)
from api.models.user.user import User
from api.models.youtube.youtube_channel import (YoutubeChannel,
                                                YoutubeChannelInfoSerializer, YoutubeChannelSerializer)
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class Campaign(models.Model):
    class Meta:
        db_table = 'api_campaign'

    STATUS_CHOICES = [
        ('new', 'New'),
        ('deleted', 'Deleted'),
    ]

    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='campaigns')

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)
    ordering_start_at = models.DateTimeField(
        null=True, blank=True, default=None)
    ordering_only_activated_products = models.BooleanField(
        blank=False, null=True, default=False)
    currency = models.CharField(max_length=255, null=True, blank=True)
    currency_sign = models.CharField(
        max_length=255, null=True, blank=True, default='$')

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, blank=True,
                              choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    facebook_page = models.ForeignKey(
        FacebookPage, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    facebook_campaign = models.JSONField(null=True, blank=True, default=dict)
    instagram_profile = models.ForeignKey(
        InstagramProfile, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    instagram_campaign = models.JSONField(null=True, blank=True, default=dict)
    youtube_channel = models.ForeignKey(
        YoutubeChannel, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    youtube_campaign = models.JSONField(null=True, blank=True, default=dict)
    meta = models.JSONField(null=True, blank=True, default=dict)
    meta_payment = models.JSONField(null=True, blank=True, default=dict)
    meta_logistic = models.JSONField(default=dict, null=True, blank=dict)

    def __str__(self):
        return self.title


class FacebookCampaignSerializer(serializers.Serializer):
    post_id = serializers.CharField(required=False, default="")
    live_video_id = serializers.CharField(required=False, default="")
    embed_url = serializers.CharField(required=False, default="")
    remark = serializers.CharField(required=False, default="")


class YoutubeChannelSerializer(serializers.Serializer):
    post_id = serializers.CharField(required=False, default="")
    live_video_id = serializers.CharField(required=False, default="")
    embed_url = serializers.CharField(required=False, default="")
    remark = serializers.CharField(required=False, default="")


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    facebook_page = FacebookPageInfoSerializer(read_only=True)
    facebook_campaign = FacebookCampaignSerializer()
    youtube_channel = YoutubeChannelInfoSerializer(read_only=True)
    youtube_campaign = YoutubeChannelSerializer()

    meta = serializers.JSONField(default=dict)
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)


class CampaignSerializerRetreive(CampaignSerializer):

    facebook_page = FacebookPageSerializer(read_only=True)
    youtube_channel = YoutubeChannelSerializer(read_only=True)


class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    list_display = [field.name for field in Campaign._meta.fields]
    search_fields = [field.name for field in Campaign._meta.fields]
