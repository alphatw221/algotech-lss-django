# Generated by Django 3.2.8 on 2021-11-17 12:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_campaign_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='status',
        ),
    ]