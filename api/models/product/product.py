from api.models.user.user import User, UserSerializer
from api.models.user.user_subscription import (UserSubscription,
                                               UserSubscriptionSerializer)
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class Product(models.Model):
    STATUS_CHOICES = [
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
        ('archived', 'Archived'),
    ]

    user_subscription = models.ForeignKey(
        UserSubscription, null=True, on_delete=models.SET_NULL, related_name='products')
    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='products')

    qty = models.IntegerField(blank=False, null=True, default=0)

    name = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    category = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    excerpt = models.TextField(null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=None)
    content = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)
    price = models.FloatField(null=True, blank=True, default=0)
    price_ori = models.FloatField(null=True, blank=True, default=0)
    tax = models.FloatField(null=True, blank=True, default=0)
    currency = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    currency_sign = models.CharField(
        max_length=255, null=True, blank=True, default='$')
    points = models.IntegerField(
        null=True, blank=True, default=0)
    model = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    sku = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    upc = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    image = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    sort_order = models.IntegerField(
        null=True, blank=True, default=0)

    order_code = models.CharField(max_length=255, null=True, blank=True)
    max_order_amount = models.IntegerField(
        blank=False, null=True, default=None)
    customer_removable = models.BooleanField(
        blank=False, null=True, default=False)
    customer_editable = models.BooleanField(
        blank=False, null=True, default=False)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, blank=True,
                              choices=STATUS_CHOICES, default='enabled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=dict, null=True, blank=True)
    meta_logistic = models.JSONField(default=dict, null=True, blank=True)
    tag = models.JSONField(default=list, null=True, blank=True)

    def __str__(self):
        return self.name



class ProductSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude=['user_subscription', 'created_by', 'category', 'image']
        read_only_fields = ['created_at', 'updated_at']



class ProductSerializerUpdate(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude=['user_subscription', 'created_by', 'category', 'image']
        read_only_fields = ['created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    # user_subscription = UserSubscriptionSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    meta = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)
    tag = serializers.JSONField(default=dict)


class ProductSerializerDropdown(ProductSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'order_code']
        read_only_fields = ['created_at', 'modified_at']


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = [field.name for field in Product._meta.fields]
    search_fields = [field.name for field in Product._meta.fields]
