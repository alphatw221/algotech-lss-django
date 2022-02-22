# Generated by Django 3.2.8 on 2022-02-22 06:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0023_user_google_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese'), ('id', 'Indonesian')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='auth_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='api_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_plan',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='api.userplan'),
        ),
    ]
