from django.contrib import admin
from djongo import models

from rest_framework import serializers

TYPE_PERCENT_OFF = 'percent_off'


class Discount(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    code = type = models.CharField(max_length=255, null=True, blank=True)

    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True)
    limitation = models.CharField(max_length=255, null=True, blank=True)
    
    meta = models.JSONField(null=True, blank=True, default=dict)
  
    def __str__(self):
        return str(self.title)





