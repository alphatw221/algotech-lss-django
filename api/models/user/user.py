
from api.models.user.facebook_info import FacebookInfoSerializer
from api.models.user.user_plan import UserPlan
from django.contrib import admin
from django.contrib.auth.models import User as AuthUser
from djongo import models
from rest_framework import serializers


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

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=512, null=True, blank=True)
    ip = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    timezone = models.CharField(
        max_length=255, null=True, blank=True, default='Asia/Singapore')

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

    def __str__(self):
        return self.name


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


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = [field.name for field in User._meta.fields]
    search_fields = [field.name for field in User._meta.fields]
