# Generated by Django 3.2.8 on 2021-12-20 04:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20211220_1231'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignproduct',
            name='price',
        ),
        migrations.RemoveField(
            model_name='campaignproduct',
            name='price_ori',
        ),
        migrations.RemoveField(
            model_name='campaignproduct',
            name='tax',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price_ori',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tax',
        ),
    ]
