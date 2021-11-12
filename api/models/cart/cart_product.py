from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.campaign.campaign_comment import CampaignComment


class CartProduct(models.Model):
    class Meta:
        db_table = 'api_cart_product'

    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.SET_NULL, related_name='cart_products')
    campaign_product = models.ForeignKey(
        CampaignProduct, blank=True, null=True, on_delete=models.SET_NULL, related_name='cart_products')
    campaign_comment = models.ForeignKey(
        CampaignComment, blank=True, null=True, on_delete=models.SET_NULL, related_name='cart_products')

    qty = models.IntegerField(blank=False, null=True, default=0)
    order_code = models.CharField(max_length=255, null=True, blank=True)

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(default=None, null=True, blank=True)
    image = models.CharField(max_length=512, null=True, blank=True)

    platform = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=None)


class CartProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartProduct
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at']

    meta = serializers.JSONField(default=dict)


class CartProductAdmin(admin.ModelAdmin):
    model = CartProduct
    list_display = [field.name for field in CartProduct._meta.fields]
    search_fields = [field.name for field in CartProduct._meta.fields]
