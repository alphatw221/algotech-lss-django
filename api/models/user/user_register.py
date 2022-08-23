from djongo import models
import business_policy


TIMEZONE_SG = 'Asia/Singapore'
class UserRegister(models.Model):
    class Meta:
        db_table = 'api_user_register'
        
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True, 
        choices=business_policy.subscription.TYPE_CHOICES, default=business_policy.subscription.TYPE_TRIAL)
    period = models.CharField(max_length=255,null=True,blank=True,default=business_policy.subscription.PERIOD_MONTH)
    created_at = models.DateTimeField(auto_now_add=True)
    timezone = models.CharField(
        max_length=255, null=True, blank=True, default=TIMEZONE_SG)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    target_country = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, blank=True, default=business_policy.subscription.COUNTRY_SG, null=True)
    meta = models.JSONField(null=True, blank=True, default=dict)
    
    def __str__(self):
        return str(self.name)