# Generated by Django 3.2.8 on 2022-08-10 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_usersubscription_meta_plugin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersubscription',
            name='meta_plugin',
        ),
    ]
