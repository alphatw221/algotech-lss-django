# Generated by Django 3.2.8 on 2022-02-10 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20220210_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubechannel',
            name='channel_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='youtubechannel',
            name='token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
