# Generated by Django 3.2.8 on 2021-11-19 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20211119_2055'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignproduct',
            name='status',
        ),
        migrations.AlterField(
            model_name='campaignproduct',
            name='type',
            field=models.CharField(blank=True, choices=[('n/a', 'Not available'), ('product', 'Added from product table'), ('quick_add', 'Added from quick-add function')], default='n/a', max_length=255),
        ),
    ]
