from djongo import models

class Developer(models.Model):
    class Meta:
        db_table = 'api_developer'

    api_key = models.CharField(max_length=255, null=True, blank=True)
    secret_key = models.CharField(max_length=255, null=True, blank=True)
    salt = models.CharField(max_length=255, null=True, blank=True)

    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)

    authorization = models.JSONField(null=False, blank=False, default=dict)

    permissions = models.JSONField(null=False, blank=False, default=dict)
    meta = models.JSONField(null=False, blank=False, default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


