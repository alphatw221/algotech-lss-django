from djongo import models
import business_policy
from rest_framework import serializers


TIMEZONE_SG = 'Asia/Singapore'

STATUS_PROCEED = 'proceed'
STATUS_COMPLETE = 'complete'
STATUS_PENDING_REFUND = 'pending_refund'
STATUS_REFUND_COMPLETE = 'refund_complete'

class UserRegister(models.Model):
    class Meta:
        db_table = 'api_user_register'
        
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True, 
        choices=business_policy.subscription.TYPE_CHOICES, default=business_policy.subscription.TYPE_TRIAL)
    status = models.CharField(max_length=255, null=True, blank=True, default=STATUS_PROCEED)

    period = models.CharField(max_length=255,null=True,blank=True,default=business_policy.subscription.PERIOD_MONTH)
    timezone = models.CharField(
        max_length=255, null=True, blank=True, default=TIMEZONE_SG)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    target_country = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, blank=True, default=business_policy.subscription.COUNTRY_SG, null=True)
    meta = models.JSONField(null=True, blank=True, default=dict)
    payment_amount = models.FloatField(null=True, blank=True, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
    
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegister
        fields = '__all__'
        read_only_fields = ['created_at', 'type', 'period', 'payment_amount']