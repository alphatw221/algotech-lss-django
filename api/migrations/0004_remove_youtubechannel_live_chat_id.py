# Generated by Django 3.2.8 on 2022-01-04 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_youtubechannel_channel_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='youtubechannel',
            name='live_chat_id',
        ),
    ]