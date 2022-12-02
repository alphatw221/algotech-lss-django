from rest_framework import serializers
from djongo import models
from api.models import user

import business_policy

STATUS_SUCCESS='success'
STATUS_FAIL='fail'
STATUS_PROCESSING='processing'

STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAIL, 'Fail'),
        (STATUS_PROCESSING, 'Processing'),
    ]

class Deal(models.Model):
    class Meta:
        db_table = 'api_deal'
    
    user_subscription = models.ForeignKey(
        user.user_subscription.UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='deals')
    original_plan = models.CharField(max_length=255, null=False, blank=False, choices=business_policy.subscription.TYPE_CHOICES)
    purchased_plan = models.CharField(max_length=255, null=False, blank=False, choices=business_policy.subscription.TYPE_CHOICES)
    total = models.FloatField(null=True, blank=True, default=0)
    status = models.CharField(max_length=255, null=True, blank=True, choices=STATUS_CHOICES)
    payer = models.ForeignKey(
        user.user.User,  null=True, on_delete=models.SET_NULL, related_name='deals')
    payment_time = models.DateTimeField()
    meta = models.JSONField(null=True, blank=True, default=dict)
    
    
    def __str__(self):
        return f'{str(self.purchased_plan)}'
    
class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        exclude = ['total']
        
    meta = serializers.JSONField(default=dict, required=False)
