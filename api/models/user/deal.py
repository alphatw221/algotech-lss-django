
from api.models.facebook.facebook_page import FacebookPageInfoSerializer
from api.models.instagram.instagram_profile import InstagramProfileInfoSerializer
from api.models.user.facebook_info import FacebookInfoSerializer
from api.models.user.promotion_code import PromotionCode
from api.models.user.user_plan import UserPlan
from django.contrib import admin
from django.contrib.auth.models import User as AuthUser
from djongo import models
from rest_framework import serializers
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializerAccountInfo
from api.models.youtube.youtube_channel import YoutubeChannelInfoSerializer


class Deal(models.Model):
    class Meta:
        db_table = 'api_deal'
    TYPE_CHOICES = [
        ('trial', 'Trial'),
        ('lite', 'Lite'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('dealer','Dealer')
    ]
    PAYMENT_STATUS = [
        ('success', 'Success'),
        ('fail', 'Fail'),
    ]
    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='deals')
    original_plan = models.CharField(max_length=255, null=False, blank=False, choices=TYPE_CHOICES)
    purchased_plan = models.CharField(max_length=255, null=False, blank=False, choices=TYPE_CHOICES)
    status = models.CharField(max_length=255, null=False, blank=False, choices=PAYMENT_STATUS)
    payer = models.ForeignKey(
        User,  null=True, on_delete=models.SET_NULL, related_name='deals')
    payment_time = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(null=True, blank=True, default=dict)
    total = models.DecimalField(decimal_places=2, blank=False, null=False)
    
    def __str__(self):
        return f'{str(self.purchased_plan)}'
    