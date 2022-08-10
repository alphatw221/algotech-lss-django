# Generated by Django 3.2.8 on 2022-08-10 07:48

from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_campaign_decimal_places'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='meta_plugin',
            field=djongo.models.fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='lang',
            field=models.CharField(choices=[('en', 'English'), ('id', 'Chinese-Simplify'), ('zh_hans', 'Chinese-Tranditional'), ('zh_hant', 'Indonesian'), ('vi', 'Vietnamese')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='facebookpage',
            name='lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese'), ('id', 'Indonesian'), ('vi', 'Vietnam')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='instagramprofile',
            name='lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese'), ('id', 'Indonesian'), ('vi', 'Vietnam')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='lang',
            field=models.CharField(choices=[('en', 'English'), ('id', 'Chinese-Simplify'), ('zh_hans', 'Chinese-Tranditional'), ('zh_hant', 'Indonesian'), ('vi', 'Vietnamese')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='buyer_lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('id', 'Chinese-Simplify'), ('zh_hans', 'Chinese-Tranditional'), ('zh_hant', 'Indonesian'), ('vi', 'Vietnamese')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('id', 'Chinese-Simplify'), ('zh_hans', 'Chinese-Tranditional'), ('zh_hant', 'Indonesian'), ('vi', 'Vietnamese')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='youtubechannel',
            name='lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese'), ('id', 'Indonesian'), ('vi', 'Vietnam')], default='en', max_length=255),
        ),
    ]
