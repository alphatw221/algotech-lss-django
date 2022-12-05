from django.conf import settings
from djongo import models
from rest_framework import serializers


class TwitchChannel(models.Model):
    class Meta:
        db_table = 'api_twitch_channel'

    name = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
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

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    token_update_by = models.CharField(max_length=255, null=True, blank=True)
    token_update_at = models.DateTimeField(null=True)
    meta = models.JSONField(null=True, blank=True, default=dict)
    payment_meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name


class TwitchChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitchChannel
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)
    meta_payment = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)


class TwitchChannelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitchChannel
        fields = ['id', 'user_name', 'name', 'remark', 'image', 'lang', 'token']
        read_only_fields = ['created_at', 'modified_at']