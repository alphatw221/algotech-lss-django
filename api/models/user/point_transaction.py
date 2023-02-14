from djongo import models
from rest_framework import serializers
from api.models.order.order import Order

from api.models.user.user_subscription import UserSubscription
from api.models.user.user import User



TYPE_CUSTOMER_PURCHASE = 'customer_purchase'
TYPE_CUSTOMER_TRANSFER = 'customer_transfer'
TYPE_SELLER_TRANSFER = 'seller_transfer'

TYPE_CHOICES = [
    TYPE_CUSTOMER_PURCHASE,
    TYPE_CUSTOMER_TRANSFER,
    TYPE_SELLER_TRANSFER
]
class PointTransaction(models.Model):
    class Meta:
        db_table = 'api_point_transaction'

    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.DO_NOTHING, related_name='point_transactions')
    
    buyer = models.ForeignKey(
        User,  null=True, on_delete=models.CASCADE, related_name='point_transactions')
    order = models.ForeignKey(
        Order,  null=True, on_delete=models.DO_NOTHING, related_name='point_transactions')
    earned = models.IntegerField(blank=True, null=True, default=0)
    used = models.IntegerField(blank=True, null=True, default=0)
    expired_at = models.DateTimeField(auto_now=False, null=True, default=None)
    used_calculated = models.BooleanField(blank=False, null=False, default=False)
    expired_calculated = models.BooleanField(blank=False, null=False, default=False)
    remark = models.CharField(null=True, blank=True, max_length=255)
    description = models.CharField(null=True, blank=True, max_length=255)
    type = models.CharField(null=True, blank=True, max_length=255, default=TYPE_CUSTOMER_PURCHASE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

api_point_transaction_template={f.get_attname():f.get_default() if f.has_default() else None for f in PointTransaction._meta.fields}