from api.models.facebook.facebook_page import (FacebookPage, FacebookPageInfoSerializer,
                                               FacebookPageSerializer)
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.facebook.facebook_page import FacebookPage
from api.models.user.user_subscription import UserSubscription


class AutoResponse(models.Model):
    class Meta:
        db_table = 'api_auto_response'

    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='auto_responses')

    facebook_page = models.ForeignKey(
        FacebookPage, null=True, on_delete=models.SET_NULL, related_name='auto_responses')

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

    meta = serializers.JSONField(default=dict)

class AutoResponseSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = AutoResponse
        exclude=['created_at', 'updated_at','user_subscription', 'facebook_page']

    meta = serializers.JSONField(default=dict)
class AutoResponseSerializerWithFacebookInfo(serializers.ModelSerializer):
    class Meta:
        model = AutoResponse
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at', 'facebook_page']

    facebook_page = FacebookPageInfoSerializer(read_only=True)
    meta = serializers.JSONField(default=dict)

class AutoResponseAdmin(admin.ModelAdmin):
    model = AutoResponse
    list_display = [field.name for field in AutoResponse._meta.fields]
    search_fields = [field.name for field in AutoResponse._meta.fields]
    readonly_fields = ('meta',)
