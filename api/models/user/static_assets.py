from djongo import models
from api.models.user.user_subscription import UserSubscription
from rest_framework import serializers


TYPE_ANIMATION='animation'

class StaticAssets(models.Model):
    class Meta:
        db_table = 'api_static_assets'

    user_subscription = models.ForeignKey(
        UserSubscription, null=True, on_delete=models.SET_NULL, related_name='assets')
    
    name = models.CharField(max_length=255, null=True, blank=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)

    type = models.CharField(max_length=255, null=True, blank=True, default=TYPE_ANIMATION)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class StaticAssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticAssets
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
