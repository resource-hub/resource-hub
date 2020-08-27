# Generated by Django 3.0.9 on 2020-08-25 09:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0006_auto_20200825_0838'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentBooking',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(
                    default=False, verbose_name='Deleted?')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(
                    auto_now=True, verbose_name='Updated at')),
                ('quantity', models.PositiveIntegerField(
                    default=1, verbose_name='Quantity')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                               to='venues.VenueContract', verbose_name='Contract')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                                to='venues.Equipment', verbose_name='Equipment')),
            ],
            options={
                'abstract': False,
            },
        ),

        migrations.RemoveField(
            model_name='venuecontract',
            name='equipment',
        ),
        migrations.AddField(
            model_name='venuecontract',
            name='equipment',
            field=models.ManyToManyField(blank=True, help_text='Services or additional equipment for the venue',
                                         through='venues.EquipmentBooking', to='venues.Equipment', verbose_name='Equipment'),
        ),
    ]
