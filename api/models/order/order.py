
# TODO: WIP
from api.models.campaign.campaign import Campaign, CampaignSerializerRetreive, CampaignSerializerWithUserSubscription
from api.models.user.user_subscription import UserSubscription
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.user.user import User

STATUS_PROCEED = 'proceed'
STATUS_COMPLETE = 'complete'
STATUS_CHOICES=[ STATUS_PROCEED,STATUS_COMPLETE ]

PAYMENT_STATUS_AWAITING_PAYMENT = 'awaiting_payment'
PAYMENT_STATUS_AWAITING_CONFIRM = 'awaiting_confirm'
PAYMENT_STATUS_FAILED = 'failed'
PAYMENT_STATUS_EXPIRED = 'expired'
PAYMENT_STATUS_PAID = 'paid'
PAYMENT_STATUS_AWAITING_REFUND = 'awaiting_refund'
PAYMENT_STATUS_REFUNDED = 'refunded'
PAYMENT_STATUS_CHOICES = [PAYMENT_STATUS_AWAITING_PAYMENT ,PAYMENT_STATUS_FAILED ,PAYMENT_STATUS_EXPIRED ,PAYMENT_STATUS_PAID ,PAYMENT_STATUS_AWAITING_REFUND ,PAYMENT_STATUS_REFUNDED ]

DELIVERY_STATUS_AWAITING_FULFILLMENT = 'awaiting_fulfillment'
DELIVERY_STATUS_AWAITING_SHIPMENT = 'awaiting_shipment'
DELIVERY_STATUS_AWAITING_PICKUP = 'awaiting_pickup'
DELIVERY_STATUS_PARTIALLY_SHIPPED = 'partially_shipped'
DELIVERY_STATUS_SHIPPED = 'shipped'
DELIVERY_STATUS_COLLECTED = 'collected'
DELIVERY_STATUS_AWAITING_RETURN = 'awaiting_return'
DELIVERY_STATUS_RETURNED = 'returned'
DELIVERY_STATUS_CHOICES=[DELIVERY_STATUS_AWAITING_FULFILLMENT ,DELIVERY_STATUS_AWAITING_SHIPMENT ,DELIVERY_STATUS_AWAITING_PICKUP ,DELIVERY_STATUS_PARTIALLY_SHIPPED ,DELIVERY_STATUS_SHIPPED ,DELIVERY_STATUS_COLLECTED ,DELIVERY_STATUS_AWAITING_RETURN ,DELIVERY_STATUS_RETURNED ]

PAYMENT_METHOD_STRIPE = 'stripe'
PAYMENT_METHOD_DIRECT = 'direct_payment'
PAYMENT_METHOD_HITPAY = 'hitpay'
PAYMENT_METHOD_PAYPAL = 'paypal'
PAYMENT_METHOD_ECPAY = 'ecpay'
PAYMENT_METHOD_PAYMONGO = 'pay_mongo'
PAYMENT_METHOD_RAPYD = 'rapyd'

SHIPPING_METHOD_DELIVERY='delivery'
SHIPPING_METHOD_PICKUP='pickup'

IMAGE_GIF = 'image/gif'
IMAGE_JPEG = 'image/jpeg'
IMAGE_JPG = 'image/jpg'
IMAGE_PNG = 'image/png'
IMAGE_SUPPORTED_TYPE = [IMAGE_JPEG, IMAGE_JPG, IMAGE_PNG]
IMAGE_MAXIMUM_SIZE = 10*1024*1024

class Order(models.Model):

    user_subscription = models.ForeignKey(
        UserSubscription, null=True, on_delete=models.SET_NULL, related_name='orders')

    campaign = models.ForeignKey(
        Campaign, null=True, on_delete=models.SET_NULL, related_name='orders')

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_img = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=255, blank=True,
                                choices=settings.SUPPORTED_PLATFORMS, default='n/a')
    platform_id = models.IntegerField(blank=True, null=True, default=None)
    buyer = models.ForeignKey(
        User, null=True, default=None, blank=True, on_delete=models.SET_NULL, related_name='orders')

    products = models.JSONField(default=dict, null=True, blank=True)
    subtotal = models.FloatField(null=True, blank=True, default=0)
    discount = models.FloatField(null=True, blank=True, default=0)
    applied_discount = models.JSONField(blank=False, null = False, default = {})
    free_delivery = models.BooleanField(
        blank=False, null=True, default=False)
    adjust_title = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    adjust_price = models.FloatField(null=True, blank=True, default=0)
    tax = models.FloatField(null=False, blank=False, default=0)
    total = models.FloatField(null=True, blank=True, default=0)

    remark = models.TextField(null=True, blank=True, default=None)

    status = models.CharField(max_length=255, null=True, blank=True, default=STATUS_PROCEED)

    # payment info
    payment_status = models.CharField(max_length=255, null=True, blank=True, default=PAYMENT_STATUS_AWAITING_PAYMENT)
    payment_method = models.CharField(
        max_length=32, blank=True, default='')
    payment_remark = models.TextField(
        blank=True, default='')
    paid_at = models.DateTimeField(
        blank=True, null=True, default=None)

    # shipping info
    delivery_status = models.CharField(max_length=255, null=True, blank=True, default=DELIVERY_STATUS_AWAITING_FULFILLMENT)
    shipping_cost = models.FloatField(null=True, blank=True, default=0)
    shipping_first_name = models.CharField(max_length=64, blank=True, default='')
    shipping_last_name = models.CharField(max_length=64, blank=True, default='')
    shipping_email = models.CharField(max_length=128, blank=True, default='')
    shipping_phone = models.CharField(max_length=64, blank=True, default='')
    shipping_postcode = models.CharField(max_length=10, blank=True, default='')
    shipping_region = models.CharField(max_length=32, blank=True, default='')
    shipping_location = models.CharField(max_length=32, blank=True, default='')
    shipping_address_1 = models.CharField(max_length=128, blank=True, default='')
    pickup_address = models.CharField(max_length=128, blank=True, default='')
    shipping_method = models.CharField(max_length=32, blank=True, default='')
    shipping_remark = models.TextField(blank=True, default='')
    shipping_date = models.DateField(blank=True, null=True, default=None)
    shipping_option = models.CharField(max_length=32, blank=True, default='')
    shipping_option_index = models.IntegerField(blank=True, null=True, default=None)
    shipping_option_data = models.JSONField(default=dict, null=False, blank=False)

    checkout_details = models.JSONField(default=dict, null=True, blank=True)
    history = models.JSONField(default=dict, null=True, blank=True)
    
    meta = models.JSONField(default=dict, null=True, blank=True)

    #point system
    meta_point = models.JSONField(default=dict, null=True, blank=True)
    points_earned = models.IntegerField(blank=True, null=True, default=0)
    points_used = models.IntegerField(blank=True, null=True, default=0)
    point_discount = models.FloatField(null=True, blank=True, default=0)
    point_expired_at = models.DateTimeField(auto_now=False, null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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