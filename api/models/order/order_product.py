
#TODO: WIP
from django.contrib import admin
from djongo import models
from rest_framework import serializers

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_order import CampaignOrder


class OrderProduct(models.Model):

    def __str__(self):
        return str(self.id)

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='order_products')

    campaign_order = models.ForeignKey(
        CampaignOrder, on_delete=models.CASCADE, related_name='order_products')

    campaign_product = models.ForeignKey(
        CampaignProduct, on_delete=models.CASCADE, related_name='order_products')

    campaign_comment = models.ForeignKey(
        CampaignComment, on_delete=models.CASCADE, related_name='order_products')

    user_id = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    order_quantity = models.IntegerField(blank=False, null=True, default=None)
    message = models.TextField(default=None, null=True, blank=True)
    order_stat = models.IntegerField(blank=False, null=True, default=None)

    meta = models.JSONField(default=None, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderProduct
        fields = '__all__'

    meta = serializers.JSONField(default=dict)


class OrderProductAdmin(admin.ModelAdmin):
    model = OrderProduct
    list_display = [field.name for field in OrderProduct._meta.fields]
    search_fields = [field.name for field in OrderProduct._meta.fields]
