# Generated by Django 3.2.16 on 2023-03-02 05:00

from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_usersubscription_require_customer_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='facebook_campaign_2',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='facebook_page_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_campaigns', to='api.facebookpage'),
        ),
        migrations.AlterField(
            model_name='buyerwallet',
            name='buyer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wallets', to='api.user'),
        ),
        migrations.AlterField(
            model_name='pointtransaction',
            name='buyer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='point_transactions', to='api.user'),
        ),
    ]