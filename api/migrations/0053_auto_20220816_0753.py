# Generated by Django 3.2.8 on 2022-08-16 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0052_campaign_stop_checkout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='lang',
            field=models.CharField(choices=[('en', 'English'), ('id', 'Indonesian'), ('zh_hans', 'Chinese-Simplify'), ('zh_hant', 'Chinese-Tranditional'), ('vi', 'Vietnamese')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='lang',
            field=models.CharField(choices=[('en', 'English'), ('id', 'Indonesian'), ('zh_hans', 'Chinese-Simplify'), ('zh_hant', 'Chinese-Tranditional'), ('vi', 'Vietnamese')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='buyer_lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('id', 'Indonesian'), ('zh_hans', 'Chinese-Simplify'), ('zh_hant', 'Chinese-Tranditional'), ('vi', 'Vietnamese')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('id', 'Indonesian'), ('zh_hans', 'Chinese-Simplify'), ('zh_hant', 'Chinese-Tranditional'), ('vi', 'Vietnamese')], default='en', max_length=255),
        ),
    ]