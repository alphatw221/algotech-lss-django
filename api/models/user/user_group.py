from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.facebook_page.facebook_page import FacebookPage, FacebookPageSerializer


class UserGroup(models.Model):
    class Meta:
        db_table = 'api_user_group'

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)
    image = models.CharField(max_length=512, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    timezone = models.CharField(
        max_length=255, null=True, blank=True, default='Asia/Singapore')

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    facebook_page = models.ManyToManyField(FacebookPage)
    meta = models.JSONField(null=True, blank=True, default=dict)
    payment_meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'

    facebook_page = FacebookPageSerializer(many=True, read_only=True)
    meta = serializers.JSONField(default=dict)
    payment_meta = serializers.JSONField(default=dict)


class UserGroupAdmin(admin.ModelAdmin):
    model = UserGroup
    list_display = [field.name for field in UserGroup._meta.fields]
    search_fields = [field.name for field in UserGroup._meta.fields]
