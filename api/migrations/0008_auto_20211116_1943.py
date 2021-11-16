# Generated by Django 3.2.8 on 2021-11-16 11:43

from django.db import migrations
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20211116_1942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='facebook_campaign',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='meta',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='youtube_campaign',
        ),
        migrations.AddField(
            model_name='autoresponse',
            name='meta',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='campaignluckydraw',
            name='candidate_set',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='campaignluckydraw',
            name='meta',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='campaignluckydraw',
            name='winner_list',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='campaignproduct',
            name='meta',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='campaignproduct',
            name='meta_logistic',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='campaignproduct',
            name='tag',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
    ]
