# Generated by Django 3.2.16 on 2023-01-16 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20230106_0622'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_time_slot',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AlterField(
            model_name='campaignproduct',
            name='image',
            field=models.CharField(blank=True, default='https://storage.googleapis.com/lss_public_bucket/static/no_image.jpeg', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.CharField(blank=True, default='https://storage.googleapis.com/lss_public_bucket/static/no_image.jpeg', max_length=255, null=True),
        ),
    ]
