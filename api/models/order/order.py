
# TODO: WIP
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class Order(models.Model):
    user_id = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(default=None, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=None, null=True, blank=True)
    product = models.JSONField(default=None, null=True, blank=True)
    history = models.JSONField(default=None, null=True, blank=True)


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)
    product = serializers.JSONField(default=dict)
    history = serializers.JSONField(default=dict)


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = [field.name for field in Order._meta.fields]
    search_fields = [field.name for field in Order._meta.fields]
