# Generated by Django 3.2.8 on 2021-12-20 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20211220_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='preorder',
            name='subtotal',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='preorder',
            name='total',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
