from django.contrib import admin
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



class Supplier(models.Model):
    class Meta:
        db_table = 'api_supplier'

    STATUS_CHOICES = [
        ('new', 'New')
    ]

    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='suppliers')

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    currency = models.CharField(max_length=255, null=True, blank=True)
    currency_sign = models.CharField(
        max_length=255, null=True, blank=True, default='$')

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, blank=True,
                              choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)
    meta_logistic = models.JSONField(default=dict, null=True, blank=dict)

    lang = models.CharField(max_length=255, blank=False, null=False,
                            choices=business_policy.subscription.LANGUAGE_CHOICES, default=business_policy.subscription.LANGUAGE_ENGLICH)
    price_unit =   models.CharField(max_length=255, null=False, blank=True,
        choices=business_policy.subscription.PRICE_UNIT_CHOICES, default=business_policy.subscription.PRICE_UNIT_UNIT)

    decimal_places = models.IntegerField( blank=False, null=False, 
        choices=business_policy.subscription.DECIMAL_CHOICES, default=business_policy.subscription.DECIMAL_001)
    
    def __str__(self):
        return str(self.name)


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    meta = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)



api_supplier_template={f.get_attname():f.get_default() if f.has_default() else None for f in Supplier._meta.fields}

