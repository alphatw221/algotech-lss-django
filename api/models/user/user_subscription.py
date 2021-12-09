from api.models.facebook.facebook_page import (FacebookPage,
                                               FacebookPageSerializer)
from api.models.instagram.instagram_profile import (
    InstagramProfile, InstagramProfileInfoSerializer)
from api.models.user.user import User, UserSerializer
from api.models.youtube.youtube_channel import (YoutubeChannel,
                                                YoutubeChannelSerializer)
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class UserSubscription(models.Model):
    class Meta:
        db_table = 'api_user_subscription'

    root_users = models.ManyToManyField(
        User, related_name='user_subscriptions')
    facebook_pages = models.ManyToManyField(
        FacebookPage, related_name='user_subscriptions')
    instagram_profiles = models.ManyToManyField(
        InstagramProfile, related_name='user_subscriptions')
    youtube_channels = models.ManyToManyField(
        YoutubeChannel, related_name='user_subscriptions')

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)
    meta_payment = models.JSONField(null=True, blank=True, default=dict)
    meta_logistic = models.JSONField(default=dict, null=True, blank=dict)
    meta_country = models.JSONField(null=True, blank=True, default=dict)


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    root_users = UserSerializer(
        many=True, read_only=True)
    facebook_pages = FacebookPageInfoSerializer(
        many=True, read_only=True)
    instagram_profiles = InstagramProfileInfoSerializer(
        many=True, read_only=True)
    youtube_channels = YoutubeChannelInfoSerializer(
        many=True, read_only=True)

    meta = serializers.JSONField(default=dict)
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)
    meta_country = serializers.JSONField(default=dict)


class UserSubscriptionSerializerSimplify(UserSubscriptionSerializer):
    class Meta:
        model = UserSubscription
        fields = ['id', 'meta', 'meta_country', 'name',
                  'description', 'remark', 'type', 'status']
        read_only_fields = ['created_at', 'modified_at']


class UserSubscriptionSerializerMeta(UserSubscriptionSerializer):
    class Meta:
        model = UserSubscription
        fields = ['meta', 'meta_country', 'meta_logistic',
                  'meta_payment']
        read_only_fields = ['created_at', 'modified_at']


class UserSubscriptionAdmin(admin.ModelAdmin):
    model = UserSubscription
    list_display = [field.name for field in UserSubscription._meta.fields]
    search_fields = [field.name for field in UserSubscription._meta.fields]
