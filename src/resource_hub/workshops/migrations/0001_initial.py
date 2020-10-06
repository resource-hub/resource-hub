# Generated by Django 3.1 on 2020-10-05 22:40

from django.db import migrations, models
import django.db.models.deletion
import recurrence.fields
import resource_hub.core.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0043_auto_20200930_0845'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Deleted?')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Deleted?')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('thumbnail_original', models.ImageField(default='images/default.png', upload_to='images/', verbose_name='Thumbnail')),
                ('workplaces', models.PositiveIntegerField()),
                ('bookable', models.BooleanField(default=True, verbose_name='Bookable?')),
                ('base_price', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.price', verbose_name='Base price')),
                ('contract_procedure', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.contractprocedure', verbose_name='Contract procedure')),
                ('gallery', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.gallery', verbose_name='Gallery')),
                ('location', models.ForeignKey(help_text="All public and current role's locations", on_delete=django.db.models.deletion.CASCADE, to='core.location', verbose_name='Location')),
                ('owner', models.ForeignKey(help_text='All available roles, be cautious when chosing a different role than your current.', on_delete=django.db.models.deletion.CASCADE, to='core.actor', verbose_name='Owner')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'location')},
            },
        ),
        migrations.CreateModel(
            name='WorkshopBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Deleted?')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('dtstart', models.DateTimeField(verbose_name='Start')),
                ('dtend', models.DateTimeField(verbose_name='End')),
                ('dtlast', models.DateTimeField()),
                ('recurrences', recurrence.fields.RecurrenceField(blank=True, verbose_name='Recurrences')),
                ('workshops', resource_hub.core.fields.CustomManyToManyField(to='workshops.Workshop', verbose_name='Workshop')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkshopEquipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('thumbnail_original', models.ImageField(upload_to='', verbose_name='Thumbnail')),
                ('quantity', models.IntegerField(verbose_name='Quantity')),
                ('price', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.price', verbose_name='Price')),
                ('workshop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='equipment', to='workshops.workshop', verbose_name='Workshop')),
            ],
        ),
        migrations.CreateModel(
            name='WorkshopPrice',
            fields=[
                ('price_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.price')),
                ('workshop_ptr', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='workshop_price', to='workshops.workshop')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.price',),
        ),
        migrations.CreateModel(
            name='WorkshopEquipmentPrice',
            fields=[
                ('price_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.price')),
                ('equipment_ptr', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='equipment_price', to='workshops.workshopequipment')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.price',),
        ),
        migrations.CreateModel(
            name='WorkshopContractProcedure',
            fields=[
                ('contractprocedure_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.contractprocedure')),
                ('workshops', models.ManyToManyField(to='workshops.Workshop', verbose_name='Workshop')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.contractprocedure',),
        ),
        migrations.CreateModel(
            name='WorkshopContract',
            fields=[
                ('contract_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.contract')),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='workshops.workshopbooking', verbose_name='Event')),
                ('equipment', models.ManyToManyField(blank=True, help_text='Services or additional equipment for the workshop', through='workshops.EquipmentBooking', to='workshops.WorkshopEquipment', verbose_name='WorkshopEquipment')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.contract',),
        ),
        migrations.AddField(
            model_name='equipmentbooking',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='equipment_bookings', to='workshops.workshopcontract', verbose_name='Contract'),
        ),
        migrations.AddField(
            model_name='equipmentbooking',
            name='equipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='equipment_bookings', to='workshops.workshopequipment', verbose_name='WorkshopEquipment'),
        ),
    ]
