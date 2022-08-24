# Generated by Django 3.2.8 on 2022-08-24 09:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0060_tiktokaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='tiktok_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaigns', to='api.tiktokaccount'),
        ),
        migrations.AddField(
            model_name='tiktokaccount',
            name='advertiser_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='tiktok_accounts',
            field=models.ManyToManyField(related_name='user_subscriptions', to='api.TikTokAccount'),
        ),
    ]
