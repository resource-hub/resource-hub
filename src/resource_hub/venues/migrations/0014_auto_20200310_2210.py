# Generated by Django 3.0.4 on 2020-03-10 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0013_venue_contract_procedure'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='venue',
        ),
        migrations.RemoveField(
            model_name='venuecontract',
            name='venues',
        ),
        migrations.AddField(
            model_name='event',
            name='venues',
            field=models.ManyToManyField(to='venues.Venue'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='equipment',
            field=models.ManyToManyField(blank=True, to='venues.Equipment'),
        ),
    ]
