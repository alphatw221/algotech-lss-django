# Generated by Django 3.2.8 on 2021-11-26 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_campaign_ordering_start_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='ordering_only_activated_products',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
