# Generated by Django 3.2.8 on 2022-03-24 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20220324_0819'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='dealer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriber_campaigns', to='api.usersubscription'),
        ),
    ]
