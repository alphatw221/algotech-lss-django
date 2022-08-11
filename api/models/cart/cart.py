from django.conf import settings
from djongo import models

from rest_framework import serializers

from api.models.campaign.campaign import Campaign
from api.models.user.user import User

SELLER_ADJUST_ADD = '+'
SELLER_ADJUST_DISCOUNT = '-'
SELLER_ADJUST_TYPES = [SELLER_ADJUST_ADD, SELLER_ADJUST_DISCOUNT]
class Cart(models.Model):
    class Meta:
        db_table = 'api_cart'
        unique_together = ['platform', 'customer_id', 'campaign']

    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.SET_NULL, related_name='carts')

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_img = models.CharField(max_length=255, null=True, blank=True)

    platform = models.CharField(max_length=255, blank=True,
                                choices=settings.SUPPORTED_PLATFORMS, default='n/a')
    platform_id = models.IntegerField(blank=True, null=True, default=None)
    
    products = models.JSONField(default=dict, null=True, blank=True)

    lock_at = models.DateTimeField(null=True, blank=True, default=None)

    seller_adjust = models.JSONField(default=[], null=True, blank=True)
    
    free_delivery = models.BooleanField(
        blank=False, null=True, default=False)

    buyer = models.ForeignKey(
        User, null=True, default=None, blank=True, on_delete=models.SET_NULL, related_name='carts')

    meta = models.JSONField(default=dict, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ['created_at', 'modified_at', 'campaign', 'buyer']

    meta = serializers.JSONField(default=dict)
    seller_adjust = serializers.JSONField(default=dict)
    products = serializers.JSONField(default=dict)

api_cart_template={f.get_attname():f.get_default() if f.has_default() else None for f in Cart._meta.fields}