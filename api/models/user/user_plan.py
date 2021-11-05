from django.contrib import admin
from djongo import models
from rest_framework import serializers


class UserPlan(models.Model):
    class Meta:
        db_table = 'api_user_plan'

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    remark = models.TextField(null=True, blank=True, default=None)
    image = models.CharField(max_length=512, null=True, blank=True)

    type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name


class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlan
        fields = '__all__'

    meta = serializers.JSONField(default=dict)


class UserPlanAdmin(admin.ModelAdmin):
    model = UserPlan
    list_display = [field.name for field in UserPlan._meta.fields]
    search_fields = [field.name for field in UserPlan._meta.fields]
