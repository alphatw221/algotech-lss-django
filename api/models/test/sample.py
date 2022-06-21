# from email.policy import default
# from django.contrib import admin
# from rest_framework import serializers
# from djongo import models


# class Sample(models.Model):
#     # _id = models.ObjectIdField(null=False)
#     title = models.CharField(max_length=255, null=True, blank=True)
#     integer = models.IntegerField(null=True, blank=True)
#     decimal = models.CharField(
#         max_length=255, null=True, blank=True, default='0.00')
#     meta = models.JSONField(
#         blank=False, null=False, default={})
#     updated_at = models.DateTimeField(auto_now=True)
#     created_at = models.DateTimeField(auto_now_add=True)


# class SampleSerializer(serializers.ModelSerializer):
#     meta = serializers.JSONField(default=dict)

#     class Meta:
#         model = Sample
#         fields = '__all__'


# class SampleAdmin(admin.ModelAdmin):
#     model = Sample
#     list_display = [field.name for field in Sample._meta.fields]
#     search_fields = [field.name for field in Sample._meta.fields]
