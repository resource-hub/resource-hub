# Generated by Django 3.0.5 on 2020-05-01 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20200501_1101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='created_by',
        ),
    ]
