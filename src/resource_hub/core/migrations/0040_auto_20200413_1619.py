# Generated by Django 3.0.4 on 2020-04-13 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20200413_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='status',
            field=models.CharField(choices=[('o', 'open'), ('c', 'closed')], default='o', max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='settlement_interval',
            field=models.IntegerField(default=7),
            preserve_default=False,
        ),
    ]