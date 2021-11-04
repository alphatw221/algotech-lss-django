from django.contrib import admin
from djongo import models
from rest_framework import serializers
from ..models.user import User


class AutoResponse(models.Model):
    class Meta:
        db_table = 'api_auto_response'

    description = models.TextField(null=True, blank=True, default=None)
    input_msg = models.TextField(null=True, blank=True, default=None)
    output_msg = models.TextField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.id)


class AutoResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoResponse
        fields = '__all__'

    meta = serializers.JSONField()


class AutoResponseAdmin(admin.ModelAdmin):
    model = AutoResponse
    list_display = [field.name for field in AutoResponse._meta.fields]
    search_fields = [field.name for field in AutoResponse._meta.fields]
