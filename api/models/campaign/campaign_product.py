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
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='campaign_products')

    name = models.CharField(max_length=255, null=True, blank=True)
    order_code = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(blank=False, null=True, default=0)
    sold_amount = models.IntegerField(blank=False, null=True, default=0)
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

    meta = models.JSONField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name


class CampaignProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignProduct
        fields = '__all__'

    meta = serializers.JSONField(default=dict)
    platform_meta = serializers.JSONField(default=dict)


class CampaignProductAdmin(admin.ModelAdmin):
    model = CampaignProduct
    list_display = [field.name for field in CampaignProduct._meta.fields]
    search_fields = [field.name for field in CampaignProduct._meta.fields]
