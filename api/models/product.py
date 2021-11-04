
#TODO: WIP
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from ..models.user import User


class Product(models.Model):

    def __str__(self):
        return self.name

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='products')

    name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(blank=False, null=False, default=0)
    image = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(blank=False, null=False, default=.0)

    meta = models.JSONField(default=None, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'

    meta = serializers.JSONField()


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = [field.name for field in Product._meta.fields]
    search_fields = [field.name for field in Product._meta.fields]
