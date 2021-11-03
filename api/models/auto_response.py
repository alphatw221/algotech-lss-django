from django.contrib import admin
from djongo import models
from rest_framework import serializers
from ..models.user import User

class AutoResponse(models.Model):

    def __str__(self):
        return str(self.id)

    message_req = models.TextField( default=None, null=True, blank=True)
    message_res = models.TextField( default=None, null=True, blank=True)
    message_type = models.TextField( default=None, null=True, blank=True)
    message_des = models.TextField( default=None, null=True, blank=True)

    meta = models.JSONField( default=None, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)



class AutoResponseSerializer(serializers.ModelSerializer):
    meta = serializers.JSONField()
    class Meta:
        model = AutoResponse
        fields = '__all__'


class AutoResponseAdmin(admin.ModelAdmin):
    model = AutoResponse
    list_display = [field.name for field in AutoResponse._meta.fields]
    search_fields = [field.name for field in AutoResponse._meta.fields]