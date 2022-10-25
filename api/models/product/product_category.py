from api.models.user.user_subscription import UserSubscription
from djongo import models
from rest_framework import serializers


class ProductCategory(models.Model):

    class Meta:
        db_table = 'api_product_category'
        unique_together = ['user_subscription', 'name']

    user_subscription = models.ForeignKey(
        UserSubscription, null=True, on_delete=models.CASCADE, related_name='product_categories')


    name = models.CharField(
        max_length=255, null=True, blank=True, default=None)
        
    description = models.TextField(null=True, blank=True, default=None)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta_logistic = models.JSONField(default=dict, null=True, blank=True)
    meta = models.JSONField(default=dict, null=True, blank=True)
    

    def __str__(self):
        return self.name


class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    meta_logistic = serializers.JSONField(default=dict)
    meta = serializers.JSONField(default=dict)
    

class ProductCategorySerializerUpdate(ProductCategorySerializer):
    class Meta:
        model = ProductCategory
        exclude = ['user_subscription']    #exclude all foreign key
        read_only_fields = ['created_at', 'updated_at']
    
api_product_category_template={f.get_attname():f.get_default() if f.has_default() else None for f in ProductCategory._meta.fields}