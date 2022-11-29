from djongo import models
from rest_framework import serializers
from api.models.order.order import Order

from api.models.user.user_subscription import UserSubscription
from api.models.user.user import User


TYPE_ORDER_TRANSACTION='order_transaction'
TYPE_TRANSFER = 'transfer'

TYPE_CHOICES = [
    (TYPE_ORDER_TRANSACTION, 'Order Transaction'),
    (TYPE_TRANSFER, 'Transfer'),
]
class BuyerPoint(models.Model):
    class Meta:
        db_table = 'api_user_point'

    user_subscription = models.ForeignKey(
        UserSubscription,  null=True, on_delete=models.SET_NULL, related_name='buyer_points')
    
    buyer = models.ForeignKey(
        User,  null=True, on_delete=models.SET_NULL, related_name='points')
    order = models.ForeignKey(
        Order,  null=True, on_delete=models.SET_NULL, related_name='buyer_points')
    earned = models.IntegerField(blank=True, null=True, default=0)
    used = models.IntegerField(blank=True, null=True, default=0)
    expired_at = models.DateTimeField(auto_now=False, null=True, default=None)
    used_calculated = models.BooleanField(blank=False, null=False, default=False)
    expired_calculated = models.BooleanField(blank=False, null=False, default=False)
    description = models.CharField(null=True, blank=True, max_length=255)
    type = models.CharField(null=True, blank=True, max_length=255, choices=TYPE_CHOICES, default=TYPE_ORDER_TRANSACTION)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BuyerPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerPoint
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

api_user_point_template={f.get_attname():f.get_default() if f.has_default() else None for f in BuyerPoint._meta.fields}