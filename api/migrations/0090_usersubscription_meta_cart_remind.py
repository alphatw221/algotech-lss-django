# Generated by Django 3.2.8 on 2022-11-21 10:46

from django.db import migrations
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0089_remove_usersubscription_meta_remind'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='meta_cart_remind',
            field=djongo.models.fields.JSONField(default=dict),
        ),
    ]
