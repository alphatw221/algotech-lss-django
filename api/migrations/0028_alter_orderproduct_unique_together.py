# Generated by Django 3.2.8 on 2021-12-21 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_auto_20211220_0747'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='orderproduct',
            unique_together={('platform', 'customer_id', 'campaign', 'campaign_product', 'pre_order', 'order')},
        ),
    ]
