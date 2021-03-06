# Generated by Django 3.0.9 on 2020-08-25 08:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0004_remove_event_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='venue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='equipment', to='venues.Venue', verbose_name='Venue'),
        ),
        migrations.AlterField(
            model_name='venuecontract',
            name='equipment',
            field=models.ManyToManyField(blank=True, help_text='Services or additional equipment for the venue', to='venues.Equipment', verbose_name='Equipment'),
        ),
    ]
