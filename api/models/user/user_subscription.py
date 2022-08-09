from email.policy import default
from pyexpat import model


from api.models.facebook.facebook_page import (FacebookPage,
                                               FacebookPageInfoSerializer, FacebookPageSerializer)
from api.models.instagram.instagram_profile import (
    InstagramProfile, InstagramProfileInfoSerializer, InstagramProfileSerializer)
from api.models.youtube.youtube_channel import (YoutubeChannel,
                                                YoutubeChannelInfoSerializer, YoutubeChannelSerializer)
from django.contrib import admin
from djongo import models
from rest_framework import serializers
import business_policy

IMAGE_NULL = 'no_image.jpeg'
IMAGE_GIF = 'image/gif'
IMAGE_JPEG = 'image/jpeg'
IMAGE_JPG = 'image/jpg'
IMAGE_PNG = 'image/png'
IMAGE_SUPPORTED_TYPE = [IMAGE_JPEG, IMAGE_JPG, IMAGE_PNG]
IMAGE_MAXIMUM_SIZE = 10*1024*1024
PLATFORM_FACEBOOK = 'facebook'
PLATFORM_INSTAGRAM = 'instagram'
PLATFORM_YOUTUBE = 'youtube'

PLATFORM_ATTR={
    PLATFORM_FACEBOOK:{'attr':'facebook_pages','serializer':FacebookPageSerializer}, 
    PLATFORM_INSTAGRAM:{'attr':'instagram_profiles','serializer':InstagramProfileSerializer}, 
    PLATFORM_YOUTUBE:{'attr':'youtube_channels','serializer':YoutubeChannelSerializer}
    }
class UserSubscription(models.Model):

    class Meta:
        db_table = 'api_user_subscription'

    facebook_pages = models.ManyToManyField(
        FacebookPage, related_name='user_subscriptions')
    instagram_profiles = models.ManyToManyField(
        InstagramProfile, related_name='user_subscriptions')
    youtube_channels = models.ManyToManyField(
        YoutubeChannel, related_name='user_subscriptions')

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True, 
        choices=business_policy.subscription.TYPE_CHOICES, default=business_policy.subscription.TYPE_TRIAL)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)
    meta_payment = models.JSONField(null=True, blank=True, default=dict)
    meta_logistic = models.JSONField(null=True, blank=True, default=dict)
    meta_country = models.JSONField(null=True, blank=True, default=dict)
    buyer_lang = models.CharField(max_length=255, blank=True,
                            choices=business_policy.subscription.LANGUAGE_CHOICES, default=business_policy.subscription.LANGUAGE_ENGLICH)
    lang = models.CharField(max_length=255, blank=True,
                            choices=business_policy.subscription.LANGUAGE_CHOICES, default=business_policy.subscription.LANGUAGE_ENGLICH)
    country = models.CharField(max_length=255, blank=True, default='SG', null=True)

    decimal_places = models.IntegerField( blank=False, null=False, 
        choices=business_policy.subscription.DECIMAL_CHOICES, default=business_policy.subscription.DECIMAL_001)
    currency =   models.CharField(max_length=255, null=True, blank=True,
        choices=business_policy.subscription.CURRENCY_CHOICES, default=business_policy.subscription.CURRENCY_SGD)
    
    price_unit =   models.CharField(max_length=255, null=False, blank=True,
        choices=business_policy.subscription.PRICE_UNIT_CHOICES, default=business_policy.subscription.PRICE_UNIT_UNIT)
        
    user_plan = models.JSONField(null=True, blank=True, default=dict)
    purchase_price = models.FloatField(null=True, blank=True, default=0)

    started_at = models.DateTimeField(null=True, blank=True, default=None)
    expired_at = models.DateTimeField(null=True, blank=True, default=None)

    dealer = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="subscribers")

    campaign_limit=models.IntegerField(blank=False, null=False, default=5)
    campaign_live_limit=models.IntegerField(blank=False, null=False, default=2)
    channel_limit=models.IntegerField(blank=False, null=False, default=1)
    product_limit=models.IntegerField(blank=False, null=False, default=10)
    order_limit=models.IntegerField(blank=False, null=False, default=100)


    def __str__(self) -> str:
        return str(self.name)
    







class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    facebook_pages = FacebookPageInfoSerializer(
        many=True, read_only=True, default=list)
    instagram_profiles = InstagramProfileInfoSerializer(
        many=True, read_only=True, default=list)
    youtube_channels = YoutubeChannelInfoSerializer(
        many=True, read_only=True, default=list)

    meta = serializers.JSONField(default=dict, required=False)
    meta_payment = serializers.JSONField(default=dict, required=False)
    meta_logistic = serializers.JSONField(default=dict, required=False)
    meta_country = serializers.JSONField(default=dict, required=False)
    user_plan = serializers.JSONField(default=dict, required=False)

class UserSubscriptionSerializerAccountInfo(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        exclude=['created_at', 'updated_at','facebook_pages','instagram_profiles','youtube_channels']

    meta = serializers.JSONField(default=dict, required=False)
    meta_payment = serializers.JSONField(default=dict, required=False)
    meta_logistic = serializers.JSONField(default=dict, required=False)
    meta_country = serializers.JSONField(default=dict, required=False)
    meta_code = serializers.JSONField(default=dict, required=False)
    user_plan = serializers.JSONField(default=dict, required=False)


class UserSubscriptionSerializerForDealerRetrieve(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        exclude=['created_at', 'updated_at','meta_payment','meta_logistic','meta_country','meta_code','meta']

    facebook_pages = FacebookPageInfoSerializer(
        many=True, read_only=True, default=list)
    instagram_profiles = InstagramProfileInfoSerializer(
        many=True, read_only=True, default=list)
    youtube_channels = YoutubeChannelInfoSerializer(
        many=True, read_only=True, default=list)
    user_plan = serializers.JSONField(default=dict, required=False)
    

class UserSubscriptionSerializerCreate(UserSubscriptionSerializer):
    class Meta:
        model = UserSubscription
        fields = ['name', 'description', 'remark', 'type', 'status', 'lang']
        read_only_fields = ['created_at', 'modified_at']

class UserSubscriptionSerializerUpgrade(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = [
            "type",
            "expired_at",
            "started_at",
            "user_plan",
            "purchase_price",
            "campaign_limit",
            "campaign_live_limit",
            "channel_limit",
            "product_limit",
            "order_limit",
        ]
        read_only_fields = ['created_at', 'modified_at']

class UserSubscriptionSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['currency','lang','buyer_lang','decimal_places']


class UserSubscriptionSerializerSimplify(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = [
            'id', 
            'meta', 
            'meta_country', 
            'name',
            'description', 
            'remark', 
            'type', 
            'status', 
            'lang',
            'expired_at',
            "started_at",
            "purchase_price",
            "campaign_limit",
            "campaign_live_limit",
            "channel_limit",
            "product_limit",
            "order_limit",
            ]
        read_only_fields = ['created_at', 'modified_at']
    
    meta = serializers.JSONField(default=dict, required=False)
    # meta_payment = serializers.JSONField(default=dict, required=False)
    # meta_logistic = serializers.JSONField(default=dict, required=False)
    meta_country = serializers.JSONField(default=dict, required=False)

class UserSubscriptionSerializerMeta(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['meta', 'meta_country', 'meta_logistic',
                  'meta_payment']
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict, required=False)
    meta_payment = serializers.JSONField(default=dict, required=False)
    meta_logistic = serializers.JSONField(default=dict, required=False)
    meta_country = serializers.JSONField(default=dict, required=False)

        
class UserSubscriptionAdmin(admin.ModelAdmin):
    model = UserSubscription
    list_display = [field.name for field in UserSubscription._meta.fields]
    search_fields = [field.name for field in UserSubscription._meta.fields]





