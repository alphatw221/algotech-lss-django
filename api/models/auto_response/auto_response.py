from api.models.facebook.facebook_page import (FacebookPage,
                                               FacebookPageSerializer)
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.facebook.facebook_page import FacebookPage


class AutoResponse(models.Model):
    class Meta:
        db_table = 'api_auto_response'

    facebook_page = models.ForeignKey(
        FacebookPage, on_delete=models.CASCADE, related_name='auto_responses')

    description = models.TextField(null=True, blank=True, default=None)
    input_msg = models.TextField(null=True, blank=True, default=None)
    output_msg = models.TextField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)


class AutoResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoResponse
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    # facebook_page = FacebookPageSerializer(read_only=True)
    meta = serializers.JSONField(default=dict)


class AutoResponseAdmin(admin.ModelAdmin):
    model = AutoResponse
    list_display = [field.name for field in AutoResponse._meta.fields]
    search_fields = [field.name for field in AutoResponse._meta.fields]
