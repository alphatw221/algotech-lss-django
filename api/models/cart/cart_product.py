from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers


class CartProduct(models.Model):
    class Meta:
        db_table = 'api_cart_product'

    TYPE_CHOICES = [
        ('n/a', 'Not available'),
        ('order_code', 'Added from order code in campaign comment'),
        ('cart', 'Added from cart page function'),
        ('lucky_draw_cart_products', 'Added from lucky draw of cart product'),
        ('lucky_draw_campaign_comments',
         'Added from lucky draw of campaign comments'),
        ('lucky_draw_campaign_likes', 'Added from lucky draw of campaign likes'),
    ]

    STATUS_CHOICES = [
        ('valid', 'Valid item for order'),
        ('ordered', 'In completed order'),
        ('staging', 'Staging for completing an order'),
        ('voided', 'Cannelled'),
    ]

    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.SET_NULL, related_name='cart_products')
    campaign_product = models.ForeignKey(
        CampaignProduct, blank=True, null=True, on_delete=models.SET_NULL, related_name='cart_products')
    campaign_comment = models.ForeignKey(
        CampaignComment, blank=True, null=True, on_delete=models.SET_NULL, related_name='cart_products')

    qty = models.IntegerField(blank=False, null=True, default=0)
    order_code = models.CharField(max_length=255, null=True, blank=True)

    platform = models.CharField(max_length=255, blank=True, default=None)
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(default=None, null=True, blank=True)

    type = models.CharField(max_length=255, blank=True,
                            choices=TYPE_CHOICES, default='n/a')
    status = models.CharField(max_length=255, blank=True,
                              choices=STATUS_CHOICES, default='valid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)


class CartProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartProduct
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)


class CartProductSerializerCreate(CartProductSerializer):

    class Meta:
        model = CartProduct
        fields = ["campaign",
                  "campaign_product",
                  "qty",
                  "platform",
                  "customer_id",
                  "customer_name",
                  "remark", ]
        read_only_fields = ['created_at', 'modified_at']


class CartProductSerializerUpdate(CartProductSerializer):

    class Meta:
        model = CartProduct
        fields = ["qty",
                  "remark", ]
        read_only_fields = ['created_at', 'modified_at']


class CartProductAdmin(admin.ModelAdmin):
    model = CartProduct
    list_display = [field.name for field in CartProduct._meta.fields]
    search_fields = [field.name for field in CartProduct._meta.fields]
