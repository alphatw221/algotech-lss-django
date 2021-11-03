from django.contrib import admin
from djongo import models
from rest_framework import serializers
from ..models.campaign import Campaign
from ..models.product import Product

class CampaignProduct(models.Model):

    def __str__(self):
        return self.name
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='products')

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='campaign_products')
    
    name = models.CharField(max_length=255, null=True, blank=True, default=None)  
    order_code = models.CharField(max_length=255, null=True, blank=True)
    product_quantity =models.IntegerField( blank=False, null=True, default=None)
    product_order_amount = models.IntegerField( blank=False, null=True, default=None)
    max_order_amount = models.IntegerField( blank=False, null=True, default=None)
    customer_removable = models.BooleanField( blank=False, null=True, default=None)
    customer_editable = models.BooleanField( blank=False, null=True, default=None)
    product_active_stat = models.IntegerField( blank=False, null=True, default=None)

    platform_meta = models.JSONField( default=None, null=True, blank=True)
    meta = models.JSONField( default=None, null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CampaignProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampaignProduct
        fields = '__all__'

    platform_meta = serializers.JSONField()
    meta = serializers.JSONField()

class CampaignProductAdmin(admin.ModelAdmin):
    model = CampaignProduct
    list_display = [field.name for field in CampaignProduct._meta.fields]
    search_fields = [field.name for field in CampaignProduct._meta.fields]