# Generated by Django 3.2.16 on 2023-02-01 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_order_shipping_time_slot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaignproduct',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
