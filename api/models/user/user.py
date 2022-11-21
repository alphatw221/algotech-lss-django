
from api.models.facebook.facebook_page import FacebookPageInfoSerializer
from api.models.instagram.instagram_profile import InstagramProfileInfoSerializer
from api.models.user.facebook_info import FacebookInfoSerializer
from api.models.user.user_plan import UserPlan
from django.contrib import admin
from django.contrib.auth.models import User as AuthUser
from djongo import models
from rest_framework import serializers

from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializerAccountInfo
from api.models.youtube.youtube_channel import YoutubeChannelInfoSerializer

import business_policy

TYPE_SELLER = 'user'
TYPE_BUYER = 'customer'

STATUS_NEW = 'new'
STATUS_VALID = 'valid'
class User(models.Model):
    class Meta:
        db_table = 'api_user'

    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('user', 'User'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('valid', 'Valid'),
    ]

    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='users')
        
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=512, null=True, blank=True) 
    ip = models.CharField(max_length=255, null=True, blank=True) #delete
    region = models.CharField(max_length=255, null=True, blank=True)
    timezone = models.CharField(
        max_length=255, null=True, blank=True, default='Asia/Singapore')  #delete

    type = models.CharField(max_length=255, null=True,
                            blank=True, choices=TYPE_CHOICES, default='customer')
    status = models.CharField(
        max_length=255, null=True, blank=True, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    facebook_info = models.JSONField(null=True, blank=True, default=dict)
    instagram_info = models.JSONField(null=True, blank=True, default=dict)
    youtube_info = models.JSONField(null=True, blank=True, default=dict)
    google_info = models.JSONField(null=True, blank=True, default=dict)
    
    user_plan = models.ForeignKey(
        UserPlan, null=True, on_delete=models.SET_NULL, related_name='users', blank=True, default=None)
    meta = models.JSONField(null=True, blank=True, default=dict)
    payment_meta = models.JSONField(null=True, blank=True, default=dict)

    auth_user = models.ForeignKey(
        AuthUser, on_delete=models.CASCADE, related_name="api_users", null=True, blank=True, default=None)

    lang = models.CharField(max_length=255, blank=False, null=False,
                            choices=business_policy.subscription.LANGUAGE_CHOICES, default=business_policy.subscription.LANGUAGE_ENGLICH)
    def __str__(self):
        return str(self.name)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    facebook_info = FacebookInfoSerializer(required=False)
    instagram_info = serializers.JSONField(default=dict)
    youtube_info = serializers.JSONField(default=dict)
    google_info = serializers.JSONField(default=dict)
    
    meta = serializers.JSONField(default=dict)
    payment_meta = serializers.JSONField(default=dict)
    

class UserSerializerAccountInfo(UserSerializer):
    user_subscription = UserSubscriptionSerializerAccountInfo(read_only=True, default=dict)

class UserSerializerForDealerList(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['auth_user','payment_meta','meta','user_plan','user_subscription','created_at','updated_at']
    facebook_info = serializers.JSONField(default=dict)
    instagram_info = serializers.JSONField(default=dict)
    youtube_info = serializers.JSONField(default=dict)
    google_info = serializers.JSONField(default=dict)
    
class UserSubscriptionSerializerDealerList(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = [
                'id', 
                'name',
                'description', 
                'remark', 
                'type', 
                'status', 
                'lang',
                'facebook_pages',
                'instagram_profiles',
                'youtube_channels',
                'user_plan',
                'expired_at',
                'users'
                ]

    facebook_pages = FacebookPageInfoSerializer(
        many=True, read_only=True, default=list)
    instagram_profiles = InstagramProfileInfoSerializer(
        many=True, read_only=True, default=list)
    youtube_channels = YoutubeChannelInfoSerializer(
        many=True, read_only=True, default=list)

    user_plan = serializers.JSONField(default=dict, required=False)
    users = UserSerializerForDealerList(many=True, read_only=True, default=list)

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = [ 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active']
        read_only_fields = [ 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active']

class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = [field.name for field in User._meta.fields]
    search_fields = [field.name for field in User._meta.fields]


api_user_template={f.get_attname():f.get_default() if f.has_default() else None for f in User._meta.fields}
