# Generated by Django 3.0.4 on 2020-04-09 11:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_auto_20200326_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='created_at',
        ),
        migrations.AddField(
            model_name='actor',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actor',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='actor',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='state',
            field=models.CharField(choices=[('i', 'initializing'), ('p', 'pending'), ('w', 'waiting'), ('r', 'running'), ('d', 'disputing'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled'), ('n', 'declined')], default='i', max_length=2),
        ),
        migrations.AlterField(
            model_name='contracttrigger',
            name='condition',
            field=models.CharField(choices=[('i', 'initializing'), ('p', 'pending'), ('w', 'waiting'), ('r', 'running'), ('d', 'disputing'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled'), ('n', 'declined')], max_length=2),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='condition',
            field=models.CharField(choices=[('i', 'initializing'), ('p', 'pending'), ('w', 'waiting'), ('r', 'running'), ('d', 'disputing'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled'), ('n', 'declined')], max_length=2),
        ),
    ]
