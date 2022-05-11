from email.policy import default
from pyexpat import model


from api.models.facebook.facebook_page import (FacebookPage,
                                               FacebookPageInfoSerializer)
from api.models.instagram.instagram_profile import (
    InstagramProfile, InstagramProfileInfoSerializer)
from api.models.youtube.youtube_channel import (YoutubeChannel,
                                                YoutubeChannelInfoSerializer)
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from django.conf import settings


class UserSubscription(models.Model):

    TYPE_CHOICES = [
        ('trial', 'Trial'),
        ('lite', 'Lite'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('dealer','Dealer')
    ]

    
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

    type = models.CharField(max_length=255, null=True, blank=True, choices=TYPE_CHOICES, default='trial')
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)
    meta_payment = models.JSONField(null=True, blank=True, default=dict)
    meta_logistic = models.JSONField(null=True, blank=True, default=dict)
    meta_country = models.JSONField(null=True, blank=True, default=dict)

    lang = models.CharField(max_length=255, blank=True,
                            choices=settings.LANGUAGES_CHOICES, default='en')
    currency =   models.CharField(max_length=255, null=True, blank=True, default='SGD')
    user_plan = models.JSONField(null=True, blank=True, default=dict)

    started_at = models.DateTimeField(null=True, blank=True, default=None)
    expired_at = models.DateTimeField(null=True, blank=True, default=None)

    dealer = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="subscribers")
    
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
            'lang'
            ]
        read_only_fields = ['created_at', 'modified_at']


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






