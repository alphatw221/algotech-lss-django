from djongo import models

from rest_framework import serializers

from api.models.user.user_subscription import UserSubscription

class DiscountCode(models.Model):
    class Meta:
        db_table = 'api_discount_code'

    # unique together ('user_subscription','code') 

    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='discount_codes')

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    code = type = models.CharField(max_length=255, null=True, blank=True)

    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True)
    limitation = models.CharField(max_length=255, null=True, blank=True)
    
    meta = models.JSONField(null=True, blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{str(self.name)} {str(self.code)}'
    

class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'
        read_only_fields = ['user_subscription', 'type', 'limitation', 'meta', 'created_at', 'updated_at']

    meta = serializers.JSONField(default=dict)
