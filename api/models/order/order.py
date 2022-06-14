
# TODO: WIP
from api.models.campaign.campaign import Campaign, CampaignSerializerRetreive, CampaignSerializerForBuyerRetreive
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.user.user import User

class Order(models.Model):
    campaign = models.ForeignKey(
        Campaign, null=True, on_delete=models.SET_NULL, related_name='orders')

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_img = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(null=True, blank=True, default=None)
    comment = models.TextField(null=True, blank=True, default=None)
    image = models.CharField(max_length=255, null=True, blank=True)
    invoice_no = models.CharField(max_length=255, null=True, blank=True)

    subtotal = models.FloatField(null=True, blank=True, default=0)
    total = models.FloatField(null=True, blank=True, default=0)
    tax = models.FloatField(null=True, blank=True, default=0)
    currency = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    currency_sign = models.CharField(
        max_length=255, null=True, blank=True, default='$')
    cost = models.FloatField(null=True, blank=True, default=0)
    cost_currency = models.CharField(
        max_length=8, null=True, blank=True, default=None)
    cost_currency_sign = models.CharField(
        max_length=255, null=True, blank=True, default='$')

    payment_first_name = models.CharField(
        max_length=64, blank=True, default='')
    payment_last_name = models.CharField(
        max_length=64, blank=True, default='')
    payment_gender = models.CharField(
        max_length=8, blank=True, default='')
    payment_company = models.CharField(
        max_length=64, blank=True, default='')
    payment_postcode = models.CharField(
        max_length=10, blank=True, default='')
    payment_region = models.CharField(
        max_length=32, blank=True, default='')
    payment_location = models.CharField(
        max_length=32, blank=True, default='')
    payment_address_1 = models.CharField(
        max_length=128, blank=True, default='')
    payment_address_2 = models.CharField(
        max_length=128, blank=True, default='')
    payment_method = models.CharField(
        max_length=32, blank=True, default='')
    payment_status = models.CharField(
        max_length=16, blank=True, default='')
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
    shipping_gender = models.CharField(
        max_length=8, blank=True, default='')
    shipping_company = models.CharField(
        max_length=64, blank=True, default='')
    shipping_postcode = models.CharField(
        max_length=10, blank=True, default='')
    shipping_region = models.CharField(
        max_length=32, blank=True, default='')
    shipping_location = models.CharField(
        max_length=32, blank=True, default='')
    shipping_address_1 = models.CharField(
        max_length=128, blank=True, default='')
    shipping_address_2 = models.CharField(
        max_length=128, blank=True, default='')
    shipping_method = models.CharField(
        max_length=32, blank=True, default='')
    shipping_status = models.CharField(
        max_length=16, blank=True, default='')
    shipping_details = models.TextField(
        blank=True, default='')
    shipping_remark = models.TextField(
        blank=True, default='')
    shipping_date = models.DateField(
        blank=True, null=True, default=None)
    shipping_time = models.TimeField(
        blank=True, null=True, default=None)
    shipping_option = models.CharField(
        max_length=32, blank=True, default='')
    tracking = models.CharField(
        max_length=32, blank=True, default='')

    platform = models.CharField(max_length=255, blank=True,
                                choices=settings.SUPPORTED_PLATFORMS, default='n/a')

    platform_id = models.IntegerField(blank=True, null=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True, default='proceed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=dict, null=True, blank=True)
    products = models.JSONField(default=dict, null=True, blank=True)
    checkout_details = models.JSONField(default=dict, null=True, blank=True)
    history = models.JSONField(default=dict, null=True, blank=True)

    adjust_title = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    adjust_price = models.FloatField(null=True, blank=True, default=0)
    free_delivery = models.BooleanField(
        blank=False, null=True, default=False)

    buyer = models.ForeignKey(
        User, null=True, default=None, blank=True, on_delete=models.SET_NULL, related_name='orders')

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    campaign = CampaignSerializerRetreive()
    meta = serializers.JSONField(default=dict)
    products = serializers.JSONField(default=dict)
    checkout_details = serializers.JSONField(default=dict)
    history = serializers.JSONField(default=dict)


# class OrderSerializerForBuyerRetrieve(serializers.ModelSerializer):

#     class Meta:
#         model = Order
#         fields = '__all__'
#         read_only_fields = ['created_at', 'modified_at']

#     campaign = CampaignSerializerForBuyerRetreive()
#     meta = serializers.JSONField(default=dict)
#     products = serializers.JSONField(default=dict)
#     checkout_details = serializers.JSONField(default=dict)
#     history = serializers.JSONField(default=dict)

class OrderSerializerUpdateShipping(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["shipping_first_name",
                  "shipping_last_name",
                  "shipping_email",
                  "shipping_phone",
                  "shipping_gender",
                  "shipping_company",
                  "shipping_postcode",
                  "shipping_region",
                  "shipping_location",
                  "shipping_address_1",
                  "shipping_address_2",
                  "shipping_method",
                  "shipping_status",
                  "shipping_details",
                  "shipping_remark",
                  "shipping_date",
                  "shipping_time", 
                  "shipping_option"]


class OrderSerializerUpdatePaymentShipping(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["shipping_first_name",
                  "shipping_last_name",
                  "shipping_email",
                  "shipping_phone",
                  "shipping_gender",
                  "shipping_company",
                  "shipping_postcode",
                  "shipping_region",
                  "shipping_location",
                  "shipping_address_1",
                  "shipping_address_2",
                  "shipping_method",
                  "shipping_status",
                  "shipping_details",
                  "shipping_remark",
                  "shipping_date",
                  "shipping_time",
                  "shipping_cost",
                  "total",
                  "payment_first_name",
                  "payment_last_name",
                  "payment_gender",
                  "payment_company",
                  "payment_postcode",
                  "payment_region",
                  "payment_location",
                  "payment_address_1",
                  "payment_address_2",
                  "payment_method",
                  "payment_status",
                  "payment_remark",
                  "remark",
                  "paid_at",
                  "status",
                  "meta" ]


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = [field.name for field in Order._meta.fields]
    search_fields = [field.name for field in Order._meta.fields]


api_order_template={f.get_attname():f.get_default() if f.has_default() else None for f in Order._meta.fields}