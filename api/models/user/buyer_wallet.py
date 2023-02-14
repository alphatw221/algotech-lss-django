from djongo import models
from rest_framework import serializers

from api.models.user.user_subscription import UserSubscription
from api.models.user.user import User


STATUS_VALID='valid'

class BuyerWallet(models.Model):
    class Meta:
        db_table = 'api_user_wallet'
        unique_together = ['user_subscription', 'buyer']

    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='buyer_wallets')
    
    buyer = models.ForeignKey(
        User,  null=True, on_delete=models.CASCADE, related_name='wallets')

    points = models.IntegerField( blank=False, null=False, default=0)
    status = models.CharField(max_length=255, blank=False, null=False, default=STATUS_VALID)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BuyerWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerWallet
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

api_user_wallet_template={f.get_attname():f.get_default() if f.has_default() else None for f in BuyerWallet._meta.fields}