# Generated by Django 3.2.16 on 2023-01-16 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20230116_0119'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_property_type',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
    ]