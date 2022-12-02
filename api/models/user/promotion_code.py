
from statistics import mode
from unicodedata import name
from django.contrib import admin
from django.contrib.auth.models import User as AuthUser
from djongo import models
from api.models.user.deal import Deal
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription

class PromotionCode(models.Model):
    class Meta:
        db_table = 'api_promotion_code'
        
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.TextField(null=True, blank=True)
    api_user = models.ForeignKey(
        User,  null=True, on_delete=models.SET_NULL, related_name='promotion_code')
    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='promotion_code')
    used_at = models.DateTimeField()
    meta = models.JSONField(null=True, blank=True, default=dict)
    deal = models.ForeignKey(Deal,  null=True, on_delete=models.SET_NULL, related_name='promotion_code')
    def __str__(self):
        return f'{str(self.name)} {str(self.code)}'
    


