# Generated by Django 3.2.8 on 2021-12-01 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_campaignluckydraw'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='status',
            field=models.CharField(blank=True, choices=[('new', 'New'), ('deleted', 'Deleted')], default='new', max_length=255),
        ),
    ]
