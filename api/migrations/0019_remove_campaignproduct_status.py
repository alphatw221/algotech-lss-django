# Generated by Django 3.2.8 on 2022-06-23 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_delete_sample'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignproduct',
            name='status',
        ),
    ]