from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.user.facebook_user import FacebookUserSerializer


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

    facebook = models.JSONField(null=True, blank=True, default=dict)
    youtube = models.JSONField(null=True, blank=True, default=dict)
    meta = models.JSONField(null=True, blank=True, default=dict)
    payment_meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    facebook = FacebookUserSerializer()
    youtube = serializers.JSONField(default=dict)
    meta = serializers.JSONField(default=dict)
    payment_meta = serializers.JSONField(default=dict)


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = [field.name for field in User._meta.fields]
    search_fields = [field.name for field in User._meta.fields]
