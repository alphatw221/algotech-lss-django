# Generated by Django 3.2.8 on 2021-11-16 11:35

from django.db import migrations, models
import time


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_campaigncomment_commented_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaigncomment',
            name='commented_at',
            field=models.IntegerField(blank=True, default=time.time, null=True),
        ),
    ]
