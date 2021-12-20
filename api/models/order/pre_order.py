from api.models.campaign.campaign import Campaign
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class PreOrder(models.Model):
    class Meta:
        db_table = 'api_pre_order'
        unique_together = ['platform', 'customer_id', 'campaign']

    campaign = models.ForeignKey(
        Campaign, null=True, on_delete=models.SET_NULL, related_name='pre_orders')

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(null=True, blank=True, default=None)
    #comment = models.TextField(null=True, blank=True, default=None)
    #image = models.CharField(max_length=255, null=True, blank=True)
    #invoice_no = models.CharField(max_length=255, null=True, blank=True)

    subtotal = models.FloatField(null=True, blank=True, default=0)
    total = models.FloatField(null=True, blank=True, default=0)
    # tax = models.CharField(
    #    max_length=255, null=True, blank=True, default='0.00')
    currency = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    currency_sign = models.CharField(
        max_length=255, null=True, blank=True, default='$')
    cost = models.CharField(
        max_length=255, null=True, blank=True, default='0.00')
    cost_currency = models.CharField(
        max_length=8, null=True, blank=True, default=None)
    cost_currency_sign = models.CharField(
        max_length=255, null=True, blank=True, default='$')

    # payment_first_name = models.CharField(
    #     max_length=64, blank=True, default='')
    # payment_last_name = models.CharField(
    #     max_length=64, blank=True, default='')
    # payment_gender = models.CharField(
    #     max_length=8, blank=True, default='')
    # payment_company = models.CharField(
    #     max_length=64, blank=True, default='')
    # payment_postcode = models.CharField(
    #     max_length=10, blank=True, default='')
    # payment_region = models.CharField(
    #     max_length=32, blank=True, default='')
    # payment_location = models.CharField(
    #     max_length=32, blank=True, default='')
    # payment_address_1 = models.CharField(
    #     max_length=128, blank=True, default='')
    # payment_address_2 = models.CharField(
    #     max_length=128, blank=True, default='')
    # payment_method = models.CharField(
    #     max_length=32, blank=True, default='')
    # payment_status = models.CharField(
    #     max_length=16, blank=True, default='')
    # payment_remark = models.TextField(
    #     blank=True, default='')
    # paid_at = models.DateTimeField(
    #     blank=True, null=True, default=None)

    # shipping_first_name = models.CharField(
    #     max_length=64, blank=True, default='')
    # shipping_last_name = models.CharField(
    #     max_length=64, blank=True, default='')
    # shipping_email = models.CharField(
    #     max_length=128, blank=True, default='')
    # shipping_phone = models.CharField(
    #     max_length=64, blank=True, default='')
    # shipping_gender = models.CharField(
    #     max_length=8, blank=True, default='')
    # shipping_company = models.CharField(
    #     max_length=64, blank=True, default='')
    # shipping_postcode = models.CharField(
    #     max_length=10, blank=True, default='')
    # shipping_region = models.CharField(
    #     max_length=32, blank=True, default='')
    # shipping_location = models.CharField(
    #     max_length=32, blank=True, default='')
    # shipping_address_1 = models.CharField(
    #     max_length=128, blank=True, default='')
    # shipping_address_2 = models.CharField(
    #     max_length=128, blank=True, default='')
    # shipping_method = models.CharField(
    #     max_length=32, blank=True, default='')
    # shipping_status = models.CharField(
    #     max_length=16, blank=True, default='')
    # shipping_details = models.TextField(
    #     blank=True, default='')
    # shipping_remark = models.TextField(
    #     blank=True, default='')
    # shipping_date = models.DateField(
    #     blank=True, null=True, default=None)
    # shipping_time = models.TimeField(
    #     blank=True, null=True, default=None)
    # tracking = models.CharField(
    #     max_length=32, blank=True, default='')

    platform = models.CharField(max_length=255, blank=True,
                                choices=settings.SUPPORTED_PLATFORMS, default='n/a')
    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=dict, null=True, blank=True)
    products = models.JSONField(default=dict, null=True, blank=True)
    checkout_details = models.JSONField(default=dict, null=True, blank=True)
    history = models.JSONField(default=dict, null=True, blank=True)

    lock_at = models.DateTimeField(null=True, blank=True, default=None)


class PreOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreOrder
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)
    products = serializers.JSONField(default=dict)
    checkout_details = serializers.JSONField(default=dict)
    history = serializers.JSONField(default=dict)


class PreOrderAdmin(admin.ModelAdmin):
    model = PreOrder
    list_display = [field.name for field in PreOrder._meta.fields]
    search_fields = [field.name for field in PreOrder._meta.fields]
