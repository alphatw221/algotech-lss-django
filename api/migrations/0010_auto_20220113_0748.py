# Generated by Django 3.2.8 on 2022-01-13 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20220112_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_cost',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='preorder',
            name='shipping_cost',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]