from django.contrib import admin
from djongo import models

from rest_framework import serializers



class Discount(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    code = type = models.CharField(max_length=255, null=True, blank=True)

    type = models.CharField(max_length=255, null=True, blank=True)

    meta = models.JSONField(null=True, blank=True, default=dict)
  
    def __str__(self):
        return str(self.title)




class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    meta = serializers.JSONField(default=dict)

