from django.contrib import admin
from djongo import models


class Mail(models.Model):
    class Meta:
        db_table = 'mail_mail'

    recipient = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    subject = models.TextField(null=True, blank=True, default=None)
    content = models.TextField(null=True, blank=True, default=None)
    sent_at = models.DateTimeField(null=True, blank=True, default=None)
    result = models.TextField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MailAdmin(admin.ModelAdmin):
    model = Mail
    list_display = [field.name for field in Mail._meta.fields]
    search_fields = [field.name for field in Mail._meta.fields]
