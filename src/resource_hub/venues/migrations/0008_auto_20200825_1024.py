# Generated by Django 3.0.9 on 2020-08-25 10:24

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0007_auto_20200825_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='size',
            field=models.PositiveIntegerField(default=10, verbose_name='Room size (squaremeters)'),
        ),
        migrations.AddField(
            model_name='venue',
            name='usage',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('o', 'other'), ('w', 'workshop')], default='o', max_length=3, verbose_name='Usage type'), default=['o'], size=None),
        ),
    ]