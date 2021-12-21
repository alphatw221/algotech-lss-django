from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.order.order import Order
from api.models.order.pre_order import PreOrder


class OrderProduct(models.Model):
    class Meta:
        db_table = 'api_order_product'
        unique_together = ['platform', 'customer_id',
                           'campaign', 'campaign_product', 'pre_order', 'order']

    TYPE_CHOICES = [
        ('n/a', 'Not available'),
        ('product', 'Product from inventory'),
        ('product-fast', 'Product from fast-add'),
        ('lucky_draw', 'Lucky Draw from inventory'),
        ('lucky_draw-fast', 'Lucky Draw from fast-add'),
    ]

    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.SET_NULL, related_name='order_products')
    campaign_product = models.ForeignKey(
        CampaignProduct, blank=True, null=True, on_delete=models.SET_NULL, related_name='order_products')
    campaign_comment = models.ForeignKey(
        CampaignComment, blank=True, null=True, on_delete=models.SET_NULL, related_name='order_products')
    order = models.ForeignKey(
        Order, blank=True, null=True, on_delete=models.CASCADE, related_name='order_products')
    pre_order = models.ForeignKey(
        PreOrder, blank=True, null=True, on_delete=models.CASCADE, related_name='order_products')
    qty = models.IntegerField(blank=False, null=True, default=0)
    order_code = models.CharField(max_length=255, null=True, blank=True)

    platform = models.CharField(max_length=255, blank=True,
                                choices=settings.SUPPORTED_PLATFORMS, default='n/a')
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(default=None, null=True, blank=True)

    type = models.CharField(max_length=255, blank=True,
                            choices=TYPE_CHOICES, default='n/a')
    status = models.CharField(max_length=255, blank=True, default='valid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)


class OrderProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderProduct
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)


class OrderProductAdmin(admin.ModelAdmin):
    model = OrderProduct
    list_display = [field.name for field in OrderProduct._meta.fields]
    search_fields = [field.name for field in OrderProduct._meta.fields]
