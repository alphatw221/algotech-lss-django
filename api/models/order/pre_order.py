from email.policy import default
from api.models.campaign.campaign import Campaign, CampaignSerializer, CampaignSerializerRetreive, CampaignSerializerWithUserSubscription
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.user.user import User


class PreOrder(models.Model):
    class Meta:
        db_table = 'api_pre_order'
        unique_together = ['platform', 'customer_id', 'campaign']

    
    campaign = models.ForeignKey(
        Campaign, null=True, on_delete=models.CASCADE, related_name='pre_orders')

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_img = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(null=True, blank=True, default=None)

    subtotal = models.FloatField(null=True, blank=True, default=0)
    total = models.FloatField(null=True, blank=True, default=0)

    payment_method = models.CharField(
        max_length=32, blank=True, default='')
    payment_remark = models.TextField(
        blank=True, default='')
    paid_at = models.DateTimeField(
        blank=True, null=True, default=None)

    shipping_cost = models.FloatField(null=True, blank=True, default=0)
    shipping_first_name = models.CharField(
        max_length=64, blank=True, default='')
    shipping_last_name = models.CharField(
        max_length=64, blank=True, default='')
    shipping_email = models.CharField(
        max_length=128, blank=True, default='')
    shipping_phone = models.CharField(
        max_length=64, blank=True, default='')
    shipping_postcode = models.CharField(
        max_length=10, blank=True, default='')
    shipping_region = models.CharField(
        max_length=32, blank=True, default='')
    shipping_location = models.CharField(
        max_length=32, blank=True, default='')
    shipping_address_1 = models.CharField(
        max_length=128, blank=True, default='')
    pickup_address = models.CharField(
        max_length=128, blank=True, default='')
    shipping_method = models.CharField(
        max_length=32, blank=True, default='')
    shipping_remark = models.TextField(
        blank=True, default='')
    shipping_date = models.DateField(
        blank=True, null=True, default=None)
    shipping_option = models.CharField(
        max_length=32, blank=True, default='')
    shipping_option_index = models.IntegerField(blank=True, null=True, default=None)
    shipping_option_data = models.JSONField(default=dict, null=False, blank=False)

    platform = models.CharField(max_length=255, blank=True,
                                choices=settings.SUPPORTED_PLATFORMS, default='n/a')
    platform_id = models.IntegerField(blank=True, null=True, default=None)
    status = models.CharField(max_length=255, null=True, blank=True, default='review')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=dict, null=True, blank=True)
    products = models.JSONField(default=dict, null=True, blank=True)
    checkout_details = models.JSONField(default=dict, null=True, blank=True)
    history = models.JSONField(default=dict, null=True, blank=True)

    lock_at = models.DateTimeField(null=True, blank=True, default=None)

    adjust_title = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    adjust_price = models.FloatField(null=True, blank=True, default=0)
    free_delivery = models.BooleanField(
        blank=False, null=True, default=False)

    buyer = models.ForeignKey(
        User, null=True, default=None, blank=True, on_delete=models.SET_NULL, related_name='pre_orders')

    discount = models.FloatField(null=False, blank=False, default=0)
    applied_discount = models.JSONField(blank=False, null = False, default = {})


class PreOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreOrder
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    campaign = CampaignSerializer()
    meta = serializers.JSONField(default=dict)
    products = serializers.JSONField(default=dict)
    checkout_details = serializers.JSONField(default=dict)
    history = serializers.JSONField(default=dict)
    applied_discount = serializers.JSONField(default=dict)
    shipping_option_data = serializers.JSONField(default=dict)
class PreOrderSerializerWithSubscription(serializers.ModelSerializer):

    class Meta:
        model = PreOrder
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    campaign = CampaignSerializerWithUserSubscription()
    meta = serializers.JSONField(default=dict)
    products = serializers.JSONField(default=dict)
    checkout_details = serializers.JSONField(default=dict)
    history = serializers.JSONField(default=dict)
    applied_discount = serializers.JSONField(default=dict)
    shipping_option_data = serializers.JSONField(default=dict)

class PreOrderSerializerUpdatePaymentShipping(serializers.ModelSerializer):

    class Meta:
        model = PreOrder
        fields = ["shipping_first_name",
                  "shipping_last_name",
                  "shipping_email",
                  "shipping_phone",
                  "shipping_postcode",
                  "shipping_region",
                  "shipping_location",
                  "shipping_address_1",
                  "shipping_method",
                  "shipping_remark",
                  "shipping_date",
                  "shipping_cost",
                  "total",
                  "payment_method",
                  "payment_remark",
                  "remark",
                  "paid_at",
                  "status",
                  "meta" ]


class PreOrderSerializerUpdateDelivery(serializers.ModelSerializer):

    class Meta:
        model = PreOrder
        fields = ["shipping_first_name",
                  "shipping_last_name",
                  "shipping_email",
                  "shipping_phone",
                  "shipping_postcode",
                  "shipping_region",
                  "shipping_location",
                  "shipping_address_1",
                  "shipping_method",
                  "shipping_remark",
                  "shipping_date",
                  "shipping_option",
                  "shipping_option_index",
                  "pickup_address",
                  "remark",
                  "shipping_option_data"
                ]
    shipping_option_data = serializers.JSONField(default=dict)
class PreOrderSerializerUpdatePickup(serializers.ModelSerializer):

    class Meta:
        model = PreOrder
        fields = [
                "shipping_first_name",
                "shipping_last_name",
                "shipping_email",
                "shipping_phone",
                "pickup_address",
                "remark",
            ]


class PreOrderAdmin(admin.ModelAdmin):
    model = PreOrder
    list_display = [field.name for field in PreOrder._meta.fields]
    search_fields = [field.name for field in PreOrder._meta.fields]


api_pre_order_template={f.get_attname():f.get_default() if f.has_default() else None for f in PreOrder._meta.fields}