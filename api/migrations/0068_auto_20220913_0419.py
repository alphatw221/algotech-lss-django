# Generated by Django 3.2.8 on 2022-09-13 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0067_campaignproduct_oversell'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deal',
            name='total',
        ),
        migrations.AddField(
            model_name='campaignproduct',
            name='overbook',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='campaignproduct',
            name='oversell',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='deal',
            name='original_plan',
            field=models.CharField(choices=[('trial', 'Trial'), ('lite', 'Lite'), ('standard', 'Standard'), ('pro', 'Pro'), ('premium', 'Premium'), ('dealer', 'Dealer')], max_length=255),
        ),
        migrations.AlterField(
            model_name='deal',
            name='purchased_plan',
            field=models.CharField(choices=[('trial', 'Trial'), ('lite', 'Lite'), ('standard', 'Standard'), ('pro', 'Pro'), ('premium', 'Premium'), ('dealer', 'Dealer')], max_length=255),
        ),
        migrations.AlterField(
            model_name='userregister',
            name='type',
            field=models.CharField(blank=True, choices=[('trial', 'Trial'), ('lite', 'Lite'), ('standard', 'Standard'), ('pro', 'Pro'), ('premium', 'Premium'), ('dealer', 'Dealer')], default='trial', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='type',
            field=models.CharField(blank=True, choices=[('trial', 'Trial'), ('lite', 'Lite'), ('standard', 'Standard'), ('pro', 'Pro'), ('premium', 'Premium'), ('dealer', 'Dealer')], default='trial', max_length=255, null=True),
        ),
    ]