
# TODO: WIP
from api.models.campaign.campaign import Campaign, CampaignSerializerRetreive, CampaignSerializerWithUserSubscription
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.user.user import User

STATUS_PENDING = 'pending'
STATUS_AWAITING_PAYMENT = 'awaiting_payment'
STATUS_AWAITING_FULFILLMENT = 'awaiting_fulfillment'
STATUS_AWAITING_SHIPMENT = 'awaiting_shipment'
STATUS_AWAITING_PICKUP = 'awaiting_pickup'
STATUS_PARTIALLY_SHIPPED = 'partially_shipped'
STATUS_SHIPPED = 'shipped'
STATUS_DISPUTED = 'disputed'
STATUS_PARTIALLY_REFUNDED = 'partially_refunded'
STATUS_REFUNDED = 'refunded'
STATUS_COMPLETE = 'complete'
STATUS_CANCELLED = 'cancelled'

#TODO update history data
STATUS_PROCEED = 'proceed' # this represent status other than complete
# STATUS_REVIEW = 'review'
# STATUS_SHIPPING_OUT = 'shipping out'
# STATUS_EXPIRED = 'expired'
# STATUS_PENDING_REFUND = 'pending_refund'

STATUS_CHOICES=[
    STATUS_PENDING ,
    STATUS_AWAITING_PAYMENT ,
    STATUS_AWAITING_FULFILLMENT ,
    STATUS_AWAITING_SHIPMENT ,
    STATUS_AWAITING_PICKUP ,
    STATUS_PARTIALLY_SHIPPED ,
    STATUS_SHIPPED ,
    STATUS_DISPUTED ,
    STATUS_PARTIALLY_REFUNDED ,
    STATUS_REFUNDED ,
    STATUS_COMPLETE ,
    STATUS_CANCELLED ,
]


PAYMENT_METHOD_STRIPE = 'stripe'
PAYMENT_METHOD_DIRECT = 'direct_payment'
PAYMENT_METHOD_HITPAY = 'hitpay'
PAYMENT_METHOD_PAYPAL = 'paypal'
PAYMENT_METHOD_ECPAY = 'ecpay'
PAYMENT_METHOD_PAYMONGO = 'pay_mongo'

SHIPPING_METHOD_DELIVERY='delivery'
SHIPPING_METHOD_PICKUP='pickup'

IMAGE_GIF = 'image/gif'
IMAGE_JPEG = 'image/jpeg'
IMAGE_JPG = 'image/jpg'
IMAGE_PNG = 'image/png'
IMAGE_SUPPORTED_TYPE = [IMAGE_JPEG, IMAGE_JPG, IMAGE_PNG]
IMAGE_MAXIMUM_SIZE = 10*1024*1024

class Order(models.Model):
    campaign = models.ForeignKey(
        Campaign, null=True, on_delete=models.SET_NULL, related_name='orders')

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

    status = models.CharField(max_length=255, null=True, blank=True, default=STATUS_AWAITING_PAYMENT)
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

    
    discount = models.FloatField(null=True, blank=True, default=0)
    applied_discount = models.JSONField(blank=False, null = False, default = {})

    tax = models.FloatField(null=False, blank=False, default=0)


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    meta = serializers.JSONField(default=dict)
    products = serializers.JSONField(default=dict)
    checkout_details = serializers.JSONField(default=dict)
    history = serializers.JSONField(default=dict)
    applied_discount = serializers.JSONField(default=dict)
    shipping_option_data = serializers.JSONField(default=dict)

class OrderWithCampaignSerializer(OrderSerializer):

    campaign = CampaignSerializerRetreive()

class OrderSerializerWithUserSubscription(OrderSerializer):

    campaign = CampaignSerializerWithUserSubscription()

class OrderSerializerUpdateShipping(serializers.ModelSerializer):

    class Meta:
        model = Order
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
                  "remark"
                  ]


    
class OrderSerializerUpdatePaymentShipping(serializers.ModelSerializer):

    class Meta:
        model = Order
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


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = [field.name for field in Order._meta.fields]
    search_fields = [field.name for field in Order._meta.fields]


api_order_template={f.get_attname():f.get_default() if f.has_default() else None for f in Order._meta.fields}