# Generated by Django 3.2.8 on 2021-11-17 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20211116_1946'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignproduct',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='campaignproduct',
            name='cost_currency',
        ),
        migrations.RemoveField(
            model_name='product',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='product',
            name='cost_currency',
        ),
        migrations.AddField(
            model_name='facebookpage',
            name='currency',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(blank=True, choices=[('customer', 'customer'), ('user', 'user')], default='customer', max_length=255, null=True),
        ),
    ]