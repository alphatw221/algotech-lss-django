# Generated by Django 3.2.8 on 2022-04-14 05:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='autoresponse',
            name='user_subscription',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auto_responses', to='api.usersubscription'),
        ),
        migrations.AlterField(
            model_name='autoresponse',
            name='facebook_page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auto_responses', to='api.facebookpage'),
        ),
    ]
