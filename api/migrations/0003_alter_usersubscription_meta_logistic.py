# Generated by Django 3.2.8 on 2022-04-08 09:36

from django.db import migrations
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20220407_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubscription',
            name='meta_logistic',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
    ]
