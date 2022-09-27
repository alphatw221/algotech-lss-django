from api.models.campaign.campaign import Campaign
from api.models.product.product import Product
from api.models.user.user import User
from django.contrib import admin
from djongo import models
from rest_framework import serializers


TYPE_PRODUCT='product'
TYPE_PRODUCT_FAST='product-fast'
TYPE_LUCKY_DRAW='lucky_draw'
TYPE_LUCKY_DRAW_FAST='lucky_draw-fast'

IMAGE_NULL = 'no_image.jpeg'
class CampaignProduct(models.Model):
    class Meta:
        db_table = 'api_campaign_product'

    TYPE_CHOICES = [
        ('n/a', 'Not available'),
        ('product', 'Product from inventory'),
        ('product-fast', 'Product from fast-add'),
        ('lucky_draw', 'Lucky Draw from inventory'),
        ('lucky_draw-fast', 'Lucky Draw from fast-add'),
    ]

    campaign = models.ForeignKey(
        Campaign, on_delete=models.SET_NULL, null=True, related_name='products')

    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='campaign_products')

    product = models.ForeignKey(
        Product, blank=True, null=True, on_delete=models.SET_NULL, related_name='campaign_products')

    qty_for_sale = models.IntegerField(blank=False, null=True, default=0)
    qty_sold = models.IntegerField(blank=False, null=True, default=0)
    qty_add_to_cart = models.IntegerField(blank=False, null=False, default=0)

    oversell = models.BooleanField(
        blank=False, null=False, default=False)
    overbook = models.BooleanField(
        blank=False, null=False, default=True)

    name = models.CharField(max_length=255, null=True,
                            blank=True, default=None)
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

    type = models.CharField(max_length=255, blank=True,
                            choices=TYPE_CHOICES, default='n/a')
    status = models.BooleanField(blank=False, null=False, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(default=dict, null=True, blank=True)
    meta_logistic = models.JSONField(default=dict, null=True, blank=True)
    tag = models.JSONField(default=dict, null=True, blank=True)


class CampaignProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignProduct
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at', 'qty_sold']

    meta = serializers.JSONField(default=dict)
    meta_logistic = serializers.JSONField(default=dict)
    tag = serializers.JSONField(default=list)


class CampaignProductSerializerAssign(serializers.ModelSerializer):
    class Meta:
        model = CampaignProduct
        fields = [
            'qty_for_sale',
            'name',
            'description',
            'price',
            'image',
            'order_code',
            'max_order_amount',
            'customer_removable',
            'customer_editable',
            'type',
            'status',
            'tag'
        ]


class CampaignProductSerializerUpdate(CampaignProductSerializer):
    class Meta:
        model = CampaignProduct
        fields = [
            'name', 
            'description', 
            'remark', 
            'qty_for_sale', 
            'customer_removable', 
            'customer_editable', 
            'max_order_amount', 
            'type', 
            'order_code', 
            'oversell', 
            'overbook'
        ]


class CampaignProductAdmin(admin.ModelAdmin):
    model = CampaignProduct
    list_display = [field.name for field in CampaignProduct._meta.fields]
    search_fields = [field.name for field in CampaignProduct._meta.fields]



api_campaign_product_template={f.get_attname():f.get_default() if f.has_default() else None for f in CampaignProduct._meta.fields}