from django.conf import settings
from djongo import models

from rest_framework import serializers

from api.models.campaign.campaign import Campaign, CampaignSerializer, CampaignSerializerWithUserSubscription
from api.models.user.user_subscription import UserSubscription
from api.models.user.user import User

SELLER_ADJUST_ADD = '+'
SELLER_ADJUST_DISCOUNT = '-'
SELLER_ADJUST_TYPES = [SELLER_ADJUST_ADD, SELLER_ADJUST_DISCOUNT]
class Cart(models.Model):
    class Meta:
        db_table = 'api_cart'
        unique_together = ['platform', 'customer_id', 'campaign']

    user_subscription = models.ForeignKey(
        UserSubscription, null=True, on_delete=models.SET_NULL, related_name='carts')

    campaign = models.ForeignKey(
        Campaign, blank=True, null=True, on_delete=models.SET_NULL, related_name='carts')

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_nickname = models.CharField(max_length=255, null=True, blank=True, default='')
    customer_img = models.CharField(max_length=255, null=True, blank=True)

    platform = models.CharField(max_length=255, blank=True, default=None)
    platform_id = models.IntegerField(blank=True, null=True, default=None)
    
    products = models.JSONField(default=dict, null=True, blank=True)

    lock_at = models.DateTimeField(null=True, blank=True, default=None)

    adjust_title = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    adjust_price = models.FloatField(null=True, blank=True, default=0)
    
    free_delivery = models.BooleanField(
        blank=False, null=True, default=False)

    buyer = models.ForeignKey(
        User, null=True, default=None, blank=True, on_delete=models.SET_NULL, related_name='carts')

    discount = models.FloatField(null=False, blank=False, default=0)
    applied_discount = models.JSONField(blank=False, null = False, default = {})
    
    tax = models.FloatField(null=False, blank=False, default=0)


    meta = models.JSONField(default=dict, null=True, blank=True)

    #point system
    # points_used = models.IntegerField(blank=True, null=True, default=0)
    # point_discount = models.FloatField(null=True, blank=True, default=0)

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
    applied_discount = serializers.JSONField(default=dict)

class CartSerializerWithCampaign(CartSerializer):
    campaign = CampaignSerializer()
    
api_cart_template={f.get_attname():f.get_default() if f.has_default() else None for f in Cart._meta.fields}