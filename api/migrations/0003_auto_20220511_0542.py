# Generated by Django 3.2.8 on 2022-05-11 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20220414_0502'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaigncomment',
            name='campaign',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='comment_id',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='commented_at',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='customer_id',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='customer_name',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='image',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='message',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='meta',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='platform',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='status',
        ),
        migrations.RemoveField(
            model_name='campaigncomment',
            name='type',
        ),
        migrations.RemoveField(
            model_name='usersubscription',
            name='meta_code',
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='currency',
            field=models.CharField(blank=True, default='SGD', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='started_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='campaigncomment',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='lang',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('zh_hans', 'Simplified Chinese'), ('zh_hant', 'Traditional Chinese'), ('id', 'Indonesian')], default='en', max_length=255),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='type',
            field=models.CharField(blank=True, choices=[('trial', 'Trial'), ('lite', 'Lite'), ('standard', 'Standard'), ('premium', 'Premium'), ('dealer', 'Dealer')], default='trial', max_length=255, null=True),
        ),
    ]