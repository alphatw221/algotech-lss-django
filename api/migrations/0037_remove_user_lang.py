# Generated by Django 3.2.8 on 2022-07-27 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_user_lang'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='lang',
        ),
    ]
