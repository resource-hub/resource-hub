# Generated by Django 3.0.3 on 2020-03-01 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20200301_1119'),
        ('venues', '0009_event_dtlast'),
    ]

    operations = [
        migrations.AddField(
            model_name='venuecontractprocedure',
            name='prices',
            field=models.ManyToManyField(to='core.Price'),
        ),
    ]
