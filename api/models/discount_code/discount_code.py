from djongo import models

from rest_framework import serializers

from api.models.user.user_subscription import UserSubscription

TYPE_PERCENT_OFF = 'percent_off'
TYPE_DEDUCT = 'deduct'

LIMITATION_SPECIFIC_CAMPAIGN = 'specific_campaign'
LIMITATION_SUBTOTAL_OVER_AMOUNT = 'subtotal_over_specific_amount'
LIMITATION_PRODUCT_OVER_NUMBER = 'product_over_specific_number'


class DiscountCode(models.Model):
    class Meta:
        db_table = 'api_discount_code'

    # unique together ('user_subscription','code') 

    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='discount_codes')

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    code = models.CharField(max_length=255, null=True, blank=True)

    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True)
    # limitation = models.CharField(max_length=255, null=True, blank=True)

    limitations = models.JSONField(null=False, blank=False, default=[])
    meta = models.JSONField(null=True, blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{str(self.name)} {str(self.code)}'
    

class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'
        read_only_fields = ['user_subscription', 'created_at', 'updated_at']

    limitations = serializers.JSONField(default=[])
    meta = serializers.JSONField(default=dict)
