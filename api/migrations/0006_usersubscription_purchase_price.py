# Generated by Django 3.2.8 on 2022-05-16 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_usersubscription_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='purchase_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
