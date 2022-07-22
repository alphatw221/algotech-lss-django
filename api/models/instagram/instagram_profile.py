from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class InstagramProfile(models.Model):
    class Meta:
        db_table = 'api_instagram_profile'

    profile_id = models.CharField(max_length=255, null=True, blank=True)
    business_id = models.CharField(max_length=255, null=True, blank=True)
    connected_facebook_page_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(null=True, blank=True, default=None)
    image = models.CharField(max_length=512, null=True, blank=True)
    lang = models.CharField(max_length=255, blank=True,
                            choices=settings.LANGUAGES, default='en')
    region = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    currency_sign = models.CharField(
        max_length=255, null=True, blank=True, default='$')
    timezone = models.CharField(
        max_length=255, null=True, blank=True, default='Asia/Singapore')
    token = models.CharField(max_length=255, null=True, blank=True)
    token_update_by = models.CharField(max_length=255, null=True, blank=True)
    token_update_at = models.DateTimeField(null=True)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)
    meta_payment = models.JSONField(null=True, blank=True, default=dict)
    meta_logistic = models.JSONField(default=dict, null=True, blank=dict)

    def __str__(self):
        return self.name


class InstagramProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramProfile
        fields = ['profile_id', 'business_id', 'name', 'remark', 'image', 'lang']
        read_only_fields = ['created_at', 'modified_at']


class InstagramProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)


class InstagramProfileAdmin(admin.ModelAdmin):
    model = InstagramProfile
    list_display = [field.name for field in InstagramProfile._meta.fields]
    search_fields = [field.name for field in InstagramProfile._meta.fields]
