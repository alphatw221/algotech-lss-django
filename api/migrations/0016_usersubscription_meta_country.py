# Generated by Django 3.2.8 on 2021-12-03 09:45

from django.db import migrations
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20211203_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='meta_country',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
    ]