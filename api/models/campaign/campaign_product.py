from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.campaign.campaign import Campaign
from api.models.product.product import Product


class CampaignProduct(models.Model):
    class Meta:
        db_table = 'api_campaign_product'

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='products')

    qty_for_sale = models.IntegerField(blank=False, null=True, default=0)
    qty_sold = models.IntegerField(blank=False, null=True, default=0)

    product = models.ForeignKey(
        Product, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaign_products')

    name = models.CharField(max_length=255, null=True,
                            blank=True, default=None)
    excerpt = models.TextField(null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=None)
    content = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)
    price = models.CharField(
        max_length=255, null=True, blank=True, default='0.00')
    price_ori = models.CharField(
        max_length=255, null=True, blank=True, default='0.00')
    tax = models.CharField(
        max_length=255, null=True, blank=True, default='0.00')
    currency = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    points = models.IntegerField(
        null=True, blank=True, default=0)
    model = models.CharField(
        max_length=32, null=True, blank=True, default=None)
    sku = models.CharField(
        max_length=32, null=True, blank=True, default=None)
    upc = models.CharField(
        max_length=32, null=True, blank=True, default=None)
    image = models.CharField(
        max_length=256, null=True, blank=True, default=None)
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
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=dict, null=True, blank=True)
    meta_logistic = models.JSONField(default=dict, null=True, blank=True)
    tag = models.JSONField(default=dict, null=True, blank=True)


class CampaignProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignProduct
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)


class CampaignProductAdmin(admin.ModelAdmin):
    model = CampaignProduct
    list_display = [field.name for field in CampaignProduct._meta.fields]
    search_fields = [field.name for field in CampaignProduct._meta.fields]
