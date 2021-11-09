from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.user.facebook_info import FacebookInfoSerializer
from api.models.user.user_plan import UserPlan


class User(models.Model):
    class Meta:
        db_table = 'api_user'

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

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    facebook_info = models.JSONField(null=True, blank=True, default=dict)
    youtube_info = models.JSONField(null=True, blank=True, default=dict)
    user_plan = models.ForeignKey(
        UserPlan, null=True, on_delete=models.SET_NULL, related_name='users')
    meta = models.JSONField(null=True, blank=True, default=dict)
    payment_meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    facebook_info = FacebookInfoSerializer(required=False)
    youtube_info = serializers.JSONField(default=dict)
    meta = serializers.JSONField(default=dict)
    payment_meta = serializers.JSONField(default=dict)


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = [field.name for field in User._meta.fields]
    search_fields = [field.name for field in User._meta.fields]
