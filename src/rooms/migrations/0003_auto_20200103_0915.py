# Generated by Django 3.0 on 2020-01-03 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_auto_20191220_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='end',
            field=models.TimeField(default='18:00:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='start',
            field=models.TimeField(default='16:00:00'),
            preserve_default=False,
        ),
    ]