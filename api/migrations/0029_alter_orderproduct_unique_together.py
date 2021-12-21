# Generated by Django 3.2.8 on 2021-12-21 07:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_alter_orderproduct_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='orderproduct',
            unique_together={('platform', 'customer_id', 'campaign',
                              'campaign_product', 'pre_order', 'order')},
        ),
    ]
