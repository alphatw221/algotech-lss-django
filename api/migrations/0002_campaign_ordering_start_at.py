# Generated by Django 3.2.8 on 2021-11-26 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='ordering_start_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]