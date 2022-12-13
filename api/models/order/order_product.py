from api.models.campaign.campaign_product import CampaignProduct, TYPE_PRODUCT
from django.conf import settings
from django.contrib import admin
from djongo import models
from rest_framework import serializers
from api.models.order.order import Order, OrderSerializerWithUserSubscription, OrderSerializer, OrderWithCampaignSerializer



class OrderProduct(models.Model):
    class Meta:
        db_table = 'api_order_product'
    
    ##inhereted from campaign_product
    

    name = models.CharField(max_length=255, null=True,
                            blank=True, default=None)
    sku = models.CharField(
        max_length=32, null=True, blank=True, default=None)
    
    order_code = models.CharField(max_length=255, blank=True, default="")
    
    price = models.FloatField(null=True, blank=True, default=0)
    
    image = models.CharField(
        max_length=256, null=True, blank=True, default=None)

    qty = models.IntegerField(blank=False, null=True, default=0)
    
    order = models.ForeignKey(
        Order, blank=True, null=True, on_delete=models.CASCADE, related_name='order_products')

    type = models.CharField(max_length=255, blank=True, default=TYPE_PRODUCT)

    subtotal = models.FloatField(null=True, blank=True, default=0)

    campaign_product = models.ForeignKey(                                                                   
        CampaignProduct, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='order_products') 

    meta = models.JSONField(null=True, blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



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


class OrderWithOrderProductSerializer(OrderSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True, default=list)

class OrderWithUserSubscriptionWithOrderProductSerializer(OrderSerializerWithUserSubscription):
    order_products = OrderProductSerializer(many=True, read_only=True, default=list)

api_order_product_template={f.get_attname():f.get_default() if f.has_default() else None for f in OrderProduct._meta.fields}