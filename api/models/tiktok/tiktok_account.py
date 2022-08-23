from djongo import models
from rest_framework import serializers


class TikTokAccount(models.Model):
    class Meta:
        db_table = 'api_tiktok_account'

    name = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(null=True, blank=True, default=None)
    image = models.CharField(max_length=512, null=True, blank=True)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    token_update_by = models.CharField(max_length=255, null=True, blank=True)
    token_update_at = models.DateTimeField(null=True)
    meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name


class TikTokAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TikTokAccount
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)

class TikTokAccountInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TikTokAccount
        fields = ['id', 'user_name', 'name', 'remark', 'image']
        read_only_fields = ['created_at', 'modified_at']