# Generated by Django 3.2.8 on 2022-08-10 07:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0045_auto_20220810_0748'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersubscription',
            name='meta_plugin',
        ),
    ]