# Generated by Django 3.2.8 on 2022-05-30 04:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_campaigncomment_main_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='tag',
        ),
    ]