# Generated by Django 3.2.16 on 2023-02-04 10:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_campaignproduct_active'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('email', 'type')},
        ),
    ]
