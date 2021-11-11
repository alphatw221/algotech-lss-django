from django.contrib import admin
from djongo import models
from rest_framework import serializers


class FacebookPage(models.Model):
    class Meta:
        db_table = 'api_facebook_page'

    page_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(null=True, blank=True, default=None)
    image = models.CharField(max_length=512, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
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
    payment_meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name


class FacebookPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookPage
        fields = '__all__'

    meta = serializers.JSONField(default=dict)
    payment_meta = serializers.JSONField(default=dict)


class FacebookPageAdmin(admin.ModelAdmin):
    model = FacebookPage
    list_display = [field.name for field in FacebookPage._meta.fields]
    search_fields = [field.name for field in FacebookPage._meta.fields]
