# Generated by Django 3.2.8 on 2022-07-06 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_staticassets'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaignluckydraw',
            name='prize',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaign_lucky_draws_prize', to='api.campaignproduct'),
        ),
    ]
