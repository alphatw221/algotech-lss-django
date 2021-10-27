from django.contrib import admin
from django.db import models
from rest_framework import serializers


class Sample(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    integer = models.IntegerField(null=True, blank=True)
    decimal = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'


class SampleAdmin(admin.ModelAdmin):
    model = Sample
    list_display = [field.name for field in Sample._meta.fields]
    search_fields = [field.name for field in Sample._meta.fields]
