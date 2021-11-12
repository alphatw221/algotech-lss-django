from django.contrib import admin
from djongo import models
from rest_framework import serializers


class UserGroup(models.Model):
    class Meta:
        db_table = 'api_user_group'

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)
    image = models.CharField(max_length=512, null=True, blank=True)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)


class UserGroupAdmin(admin.ModelAdmin):
    model = UserGroup
    list_display = [field.name for field in UserGroup._meta.fields]
    search_fields = [field.name for field in UserGroup._meta.fields]
