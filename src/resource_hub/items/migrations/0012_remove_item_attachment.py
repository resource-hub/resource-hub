# Generated by Django 3.0.9 on 2020-09-24 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0011_auto_20200527_1102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='attachment',
        ),
    ]
