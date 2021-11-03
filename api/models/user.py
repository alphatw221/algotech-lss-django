from django.contrib import admin
from djongo import models
from rest_framework import serializers


class User(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    ip = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(default=None, null=True, blank=True)

    payment_meta = models.JSONField(default=None, null=True, blank=True)
    meta = models.JSONField(default=None, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    meta = serializers.JSONField()
    payment_meta = serializers.JSONField()


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = [field.name for field in User._meta.fields]
    search_fields = [field.name for field in User._meta.fields]
