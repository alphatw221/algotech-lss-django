from djongo import models

from rest_framework import serializers

from api.models.user.user_subscription import UserSubscription



TYPE_CART_REFERAL = 'cart_referal'
TYPE_GENERAL = 'general'

TYPE_CHOICES = [TYPE_CART_REFERAL, TYPE_GENERAL]
DISCOUNT_TYPE_PERCENT_OFF = 'percent_off'
DISCOUNT_TYPE_DEDUCT = 'deduct'

LIMITATION_SPECIFIC_CAMPAIGN = 'specific_campaign'
LIMITATION_SPECIFIC_BUYER_NAME = 'specific_buyer_name'
LIMITATION_SPECIFIC_BUYER_EMAIL = 'specific_buyer_email'
LIMITATION_SUBTOTAL_OVER_AMOUNT = 'subtotal_over_specific_amount'
LIMITATION_PRODUCT_OVER_NUMBER = 'product_over_specific_number'
LIMITATION_DISCOUNT_CODE_USABLE_TIME = 'discount_code_usable_time'
LIMITATION_NEW_BUYER_ONLY = 'new_buyer_only'
LIMITATION_BUYER_USAGE_TIMES = 'buyer_usage_times'

class DiscountCode(models.Model):
    class Meta:
        db_table = 'api_discount_code'
        unique_together=('user_subscription','code')


    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='discount_codes')

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    code = models.CharField(max_length=255, null=True, blank=True)

    period_enabled = models.BooleanField(null=False, blank=False, default=True)
    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=False, blank=False, default=TYPE_GENERAL)
    discount_type = models.CharField(max_length=255, null=True, blank=True)

    limitations = models.JSONField(null=False, blank=False, default=[])

    applied_count = models.IntegerField( blank=False, null=False, default=0)
    used_count = models.IntegerField( blank=False, null=False, default=0)
    
    meta = models.JSONField(null=True, blank=True, default=dict)

    buyer_usage = models.JSONField(null=True, blank=True, default=dict)
    # buyer_applied = models.JSONField(null=True, blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{str(self.name)} {str(self.code)}'
    

class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'applied_count', 'used_count']

    limitations = serializers.JSONField(default=[])
    meta = serializers.JSONField(default=dict)
    buyer_usage = serializers.JSONField(default=dict)