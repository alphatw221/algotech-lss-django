from email.policy import default
from re import T
from api.models.facebook.facebook_page import (FacebookPage,
                                               FacebookPageInfoSerializer, FacebookPageSerializer)

from api.models.instagram.instagram_profile import (
    InstagramProfile, InstagramProfileSerializer, InstagramProfileInfoSerializer)
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializer
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

    user_subscription = models.ForeignKey(
        UserSubscription, null=True, on_delete=models.SET_NULL, related_name='campaigns')

    dealer = models.ForeignKey(
        UserSubscription, null=True, on_delete=models.SET_NULL, related_name='subscriber_campaigns')

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
        return str(self.title)


class FacebookCampaignSerializer(serializers.Serializer):
    post_id = serializers.CharField(required=False, default="", allow_blank=True)
    comment_capture_since = serializers.FloatField(required=False, default=1)
    remark = serializers.CharField(required=False, default="", allow_blank=True)


class YoutubeCampaignSerializer(serializers.Serializer):
    live_video_id = serializers.CharField(required=False, default="", allow_blank=True)
    live_chat_id = serializers.CharField(required=False, default="", allow_blank=True)
    is_failed = serializers.BooleanField(required=False, default=False)
    latest_comment_time = serializers.FloatField(required=False, default=1)
    remark = serializers.CharField(required=False, default="", allow_blank=True)
    next_page_token = serializers.CharField(required=False, default="", allow_blank=True)
    access_token = serializers.CharField(required=False, default="", allow_blank=True)
    refresh_token = serializers.CharField(required=False, default="", allow_blank=True)
    last_refresh_timestamp = serializers.FloatField(required=False, default=1)


class InstagramCampaignSerializer(serializers.Serializer):
    live_media_id = serializers.CharField(required=False, default="", allow_blank=True)
    remark = serializers.CharField(required=False, default="", allow_blank=True)
    last_create_message_id = serializers.CharField(required=False, default="", allow_blank=True)
    is_failed = serializers.BooleanField(required=False, default=False)


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    facebook_page = FacebookPageInfoSerializer(default=dict)
    facebook_campaign = FacebookCampaignSerializer(default=dict)
    youtube_channel = YoutubeChannelInfoSerializer(default=dict)
    youtube_campaign = YoutubeCampaignSerializer(default=dict)
    instagram_profile = InstagramProfileInfoSerializer(default=dict)
    instagram_campaign = InstagramCampaignSerializer(default=dict)

    meta = serializers.JSONField(default=dict)
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)


class CampaignSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        # fields = '__all__'
        exclude = ['facebook_page', 'youtube_channel', 'instagram_profile']
        read_only_fields = ['created_at', 'modified_at']

    facebook_campaign = FacebookCampaignSerializer(default=dict)
    youtube_campaign = YoutubeCampaignSerializer(default=dict)
    instagram_campaign = InstagramCampaignSerializer(default=dict)

    meta = serializers.JSONField(default={"allow_checkout": 1})
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)


class CampaignSerializerEdit(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        # fields = '__all__'
        exclude = ['facebook_page', 'youtube_channel', 'instagram_profile']
        read_only_fields = ['created_at', 'modified_at']

    facebook_campaign = FacebookCampaignSerializer(default=dict)
    youtube_campaign = YoutubeCampaignSerializer(default=dict)
    instagram_campaign = InstagramCampaignSerializer(default=dict)

    meta = serializers.JSONField(default={"allow_checkout": 1})
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)


class CampaignSerializerUpdate(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ['title', 'start_at', 'end_at', 'meta', 'meta_payment', 'meta_logistic']

    meta = serializers.JSONField(default={"allow_checkout": 1})
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)


class CampaignSerializerRetreive(CampaignSerializer):
    facebook_page = FacebookPageSerializer(read_only=True)
    youtube_channel = YoutubeChannelSerializer(read_only=True)
    instagram_profile = InstagramProfileSerializer(read_only=True)

class CampaignSerializerWithUserSubscription(CampaignSerializer):

    user_subscription = UserSubscriptionSerializer(read_only=True)
    facebook_page = FacebookPageSerializer(read_only=True)
    youtube_channel = YoutubeChannelSerializer(read_only=True)
    instagram_profile = InstagramProfileSerializer(read_only=True)

class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    list_display = [field.name for field in Campaign._meta.fields]
    search_fields = [field.name for field in Campaign._meta.fields]
