# Generated by Django 3.2.8 on 2022-12-12 08:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_campaign_supplier_subscripiton'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='supplier_subscripiton',
            new_name='supplier',
        ),
    ]
