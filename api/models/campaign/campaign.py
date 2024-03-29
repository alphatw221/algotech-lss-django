from django.contrib import admin
from api.models.product.product_category import ProductCategorySerializer
from djongo import models


from rest_framework import serializers

from api.models.facebook.facebook_page import (FacebookPage,
                                               FacebookPageInfoSerializer, FacebookPageSerializer)

from api.models.instagram.instagram_profile import (
    InstagramProfile, InstagramProfileSerializer, InstagramProfileInfoSerializer)
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializer
from api.models.youtube.youtube_channel import (YoutubeChannel,
                                                YoutubeChannelInfoSerializer, YoutubeChannelSerializer)
from api.models.twitch.twitch_channel import TwitchChannel, TwitchChannelSerializer, TwitchChannelInfoSerializer
from api.models.tiktok.tiktok_account import TikTokAccount, TikTokAccountSerializer, TikTokAccountInfoSerializer

import business_policy

IMAGE_NULL='no_image.jpeg'
IMAGE_GIF = 'image/gif'
IMAGE_JPEG = 'image/jpeg'
IMAGE_JPG = 'image/jpg'
IMAGE_PNG = 'image/png'
IMAGE_SUPPORTED_TYPE = [IMAGE_JPEG, IMAGE_JPG, IMAGE_PNG]
IMAGE_MAXIMUM_SIZE = 10*1024*1024

STATUS_HISTORY = 'history'
STATUS_SCHEDULED = 'scheduled'
STATUS_ONGOING = 'ongoing'

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
    supplier = models.ForeignKey(
        UserSubscription, null=True, on_delete=models.SET_NULL, related_name='cooperator_campaigns')
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

    sub_facebook_page = models.ForeignKey(
        FacebookPage, blank=True, null=True, on_delete=models.SET_NULL, related_name='sub_campaigns')
    sub_facebook_campaign = models.JSONField(null=True, blank=True, default=dict)

    sub_facebook_page_3 = models.ForeignKey(
        FacebookPage, blank=True, null=True, on_delete=models.SET_NULL, related_name='sub_campaigns_3')
    sub_facebook_campaign_3 = models.JSONField(null=True, blank=True, default=dict)

    sub_facebook_page_4 = models.ForeignKey(
        FacebookPage, blank=True, null=True, on_delete=models.SET_NULL, related_name='sub_campaigns_4')
    sub_facebook_campaign_4 = models.JSONField(null=True, blank=True, default=dict)

    sub_facebook_page_5 = models.ForeignKey(
        FacebookPage, blank=True, null=True, on_delete=models.SET_NULL, related_name='sub_campaigns_5')
    sub_facebook_campaign_5 = models.JSONField(null=True, blank=True, default=dict)

    sub_facebook_page_6 = models.ForeignKey(
        FacebookPage, blank=True, null=True, on_delete=models.SET_NULL, related_name='sub_campaigns_6')
    sub_facebook_campaign_6 = models.JSONField(null=True, blank=True, default=dict)

    instagram_profile = models.ForeignKey(
        InstagramProfile, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    instagram_campaign = models.JSONField(null=True, blank=True, default=dict)
    youtube_channel = models.ForeignKey(
        YoutubeChannel, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    youtube_campaign = models.JSONField(null=True, blank=True, default=dict)

    twitch_channel = models.ForeignKey(
        TwitchChannel, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    twitch_campaign = models.JSONField(null=True, blank=True, default=dict)

    tiktok_account = models.ForeignKey(
        TikTokAccount, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaigns')
    tiktok_campaign = models.JSONField(null=True, blank=True, default=dict)

    meta = models.JSONField(null=True, blank=True, default=dict)
    meta_payment = models.JSONField(null=True, blank=True, default=dict)
    meta_logistic = models.JSONField(default=dict, null=True, blank=dict)
    meta_reply = models.JSONField(null=False, blank=False, default=dict)
    meta_point = models.JSONField(null=False, blank=False, default=dict)


    lang = models.CharField(max_length=255, blank=False, null=False,
                            choices=business_policy.subscription.LANGUAGE_CHOICES, default=business_policy.subscription.LANGUAGE_ENGLICH)
    price_unit =   models.CharField(max_length=255, null=False, blank=True,
        choices=business_policy.subscription.PRICE_UNIT_CHOICES, default=business_policy.subscription.PRICE_UNIT_UNIT)

    decimal_places = models.IntegerField( blank=False, null=False, 
        choices=business_policy.subscription.DECIMAL_CHOICES, default=business_policy.subscription.DECIMAL_001)
    
    stop_checkout = models.BooleanField(
        blank=False, null=False, default=False)
    
    # discounts = models.ArrayField(model_container=Discount, blank=False, null = False, default = [])
    priority = models.IntegerField( blank=False, null=False, default=1)
    silent_count = models.IntegerField( blank=False, null=False, default=0)
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

class TwitchCampaignSerializer(serializers.Serializer):
    token = serializers.CharField(required=False, default="", allow_blank=True)
    channel_name = serializers.CharField(required=False, default="", allow_blank=True)
    broadcaster_id = serializers.CharField(required=False, default="", allow_blank=True)
    moderator_id = serializers.CharField(required=False, default="", allow_blank=True)

class TiktokCampaignSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, default="", allow_blank=True)

class SupplierUserSubscriptionAccountInfo(UserSubscriptionSerializer):

    class Meta:
        model = UserSubscription
        fields = ['id', 'product_categories']
        
    product_categories = ProductCategorySerializer(many=True, read_only=True, default=list)

    
class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    supplier = SupplierUserSubscriptionAccountInfo(read_only=True, default=dict)
    facebook_page = FacebookPageInfoSerializer(default=dict)
    facebook_campaign = FacebookCampaignSerializer(default=dict)
    sub_facebook_page = FacebookPageInfoSerializer(default=dict)
    sub_facebook_campaign = FacebookCampaignSerializer(default=dict)
    sub_facebook_page_3 = FacebookPageInfoSerializer(default=dict)
    sub_facebook_campaign_3 = FacebookCampaignSerializer(default=dict)
    sub_facebook_page_4 = FacebookPageInfoSerializer(default=dict)
    sub_facebook_campaign_4 = FacebookCampaignSerializer(default=dict)
    sub_facebook_page_5 = FacebookPageInfoSerializer(default=dict)
    sub_facebook_campaign_5 = FacebookCampaignSerializer(default=dict)
    sub_facebook_page_6 = FacebookPageInfoSerializer(default=dict)
    sub_facebook_campaign_6 = FacebookCampaignSerializer(default=dict)

    youtube_channel = YoutubeChannelInfoSerializer(default=dict)
    youtube_campaign = YoutubeCampaignSerializer(default=dict)
    instagram_profile = InstagramProfileInfoSerializer(default=dict)
    instagram_campaign = InstagramCampaignSerializer(default=dict)
    twitch_channel = TwitchChannelInfoSerializer(default=dict)
    twitch_campaign = TwitchCampaignSerializer(default=dict)
    tiktok_campaign = TiktokCampaignSerializer(default=dict)

    meta = serializers.JSONField(default=dict)
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)
    meta_reply = serializers.JSONField(default=dict)
    meta_point = serializers.JSONField(default=dict)

class CampaignSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        # fields = '__all__'
        exclude = ['facebook_page', 'youtube_channel', 'instagram_profile', 'dealer']
        read_only_fields = ['created_at', 'updated_at']

    facebook_campaign = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign_3 = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign_4 = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign_5 = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign_6 = FacebookCampaignSerializer(default=dict)


    youtube_campaign = YoutubeCampaignSerializer(default=dict)
    instagram_campaign = InstagramCampaignSerializer(default=dict)
    twitch_campaign = TwitchCampaignSerializer(default=dict)
    tiktok_campaign = TiktokCampaignSerializer(default=dict)

    meta = serializers.JSONField(default={"allow_checkout": 1})
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)
    meta_reply = serializers.JSONField(default=dict)
    meta_point = serializers.JSONField(default=dict)

class CampaignSerializerEdit(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        # fields = '__all__'
        exclude = ['facebook_page', 'youtube_channel', 'instagram_profile', 'dealer']
        read_only_fields = ['created_at', 'updated_at']

    facebook_campaign = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign_3 = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign_4 = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign_5 = FacebookCampaignSerializer(default=dict)
    sub_facebook_campaign_6 = FacebookCampaignSerializer(default=dict)

    youtube_campaign = YoutubeCampaignSerializer(default=dict)
    instagram_campaign = InstagramCampaignSerializer(default=dict)
    twitch_campaign = TwitchCampaignSerializer(default=dict)
    tiktok_campaign = TiktokCampaignSerializer(default=dict)

    meta = serializers.JSONField(default={"allow_checkout": 1})
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)
    

class CampaignSerializerUpdate(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ['title', 'start_at', 'end_at', 'meta', 'meta_payment', 'meta_logistic', 'lang', 'currency', 'price_unit', 'decimal_places', 'meta_reply', 'meta_point']

    meta = serializers.JSONField(default={"allow_checkout": 1})
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)
    meta_reply = serializers.JSONField(default=dict)
    meta_point = serializers.JSONField(default=dict)

class CampaignSerializerRetreive(CampaignSerializer):
    facebook_page = FacebookPageSerializer(read_only=True)
    sub_facebook_page = FacebookPageSerializer(read_only=True)
    sub_facebook_page_3 = FacebookPageSerializer(read_only=True)
    sub_facebook_page_4 = FacebookPageSerializer(read_only=True)
    sub_facebook_page_5 = FacebookPageSerializer(read_only=True)
    sub_facebook_page_6 = FacebookPageSerializer(read_only=True)

    youtube_channel = YoutubeChannelSerializer(read_only=True)
    instagram_profile = InstagramProfileSerializer(read_only=True)
    twitch_channel = TwitchChannelSerializer(read_only=True)

class CampaignSerializerWithUserSubscription(CampaignSerializer):

    user_subscription = UserSubscriptionSerializer(read_only=True)
    facebook_page = FacebookPageSerializer(read_only=True)
    sub_facebook_page = FacebookPageSerializer(read_only=True)
    sub_facebook_page_3 = FacebookPageSerializer(read_only=True)
    sub_facebook_page_4 = FacebookPageSerializer(read_only=True)
    sub_facebook_page_5 = FacebookPageSerializer(read_only=True)
    sub_facebook_page_6 = FacebookPageSerializer(read_only=True)

    youtube_channel = YoutubeChannelSerializer(read_only=True)
    instagram_profile = InstagramProfileSerializer(read_only=True)
    twitch_channel = TwitchChannelSerializer(read_only=True)

class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    list_display = [field.name for field in Campaign._meta.fields]
    search_fields = [field.name for field in Campaign._meta.fields]

class CampaignOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['id', 'title']
        read_only_fields = ['id', 'title']


api_campaign_template={f.get_attname():f.get_default() if f.has_default() else None for f in Campaign._meta.fields}

