# Generated by Django 3.0.5 on 2020-05-22 12:09

from django.db import migrations, models
import django.db.models.deletion
import recurrence.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20200522_1209'),
        ('venues', '0002_auto_20200429_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='name',
            field=models.CharField(max_length=128, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='price',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.Price', verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='quantity',
            field=models.IntegerField(verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='thumbnail_original',
            field=models.ImageField(upload_to='', verbose_name='Thumbnail'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='venue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='venues.Venue', verbose_name='Venue'),
        ),
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='venues.EventCategory', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='event',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='event',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_created_by', to='core.Actor', verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.CharField(max_length=128, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='event',
            name='dtend',
            field=models.DateTimeField(verbose_name='End'),
        ),
        migrations.AlterField(
            model_name='event',
            name='dtstart',
            field=models.DateTimeField(verbose_name='Start'),
        ),
        migrations.AlterField(
            model_name='event',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Deleted?'),
        ),
        migrations.AlterField(
            model_name='event',
            name='is_public',
            field=models.BooleanField(blank=True, default=True, verbose_name='Public?'),
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_actor', to='core.Actor', verbose_name='Organizer'),
        ),
        migrations.AlterField(
            model_name='event',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(blank=True, verbose_name='Recurrences'),
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(blank=True, to='venues.EventTag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='event',
            name='thumbnail_original',
            field=models.ImageField(upload_to='images/', verbose_name='Thumbnail'),
        ),
        migrations.AlterField(
            model_name='event',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
        migrations.AlterField(
            model_name='event',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_updated_by', to='core.Actor', verbose_name='Updated by'),
        ),
        migrations.AlterField(
            model_name='event',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='event',
            name='venues',
            field=models.ManyToManyField(to='venues.Venue', verbose_name='Venues'),
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='name',
            field=models.CharField(max_length=64, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='eventtag',
            name='name',
            field=models.CharField(max_length=64, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='bookable',
            field=models.BooleanField(default=True, verbose_name='Bookable?'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='contract_procedure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.ContractProcedure', verbose_name='Contract procedure'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='gallery',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Gallery', verbose_name='Gallery'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Deleted?'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='location',
            field=models.ForeignKey(help_text="All public and current role's locations", on_delete=django.db.models.deletion.CASCADE, to='core.Location', verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='owner',
            field=models.ForeignKey(help_text='All available roles, be cautious when chosing a different role than your current.', on_delete=django.db.models.deletion.CASCADE, to='core.Actor', verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='price',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.Price', verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='slug',
            field=models.SlugField(verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='thumbnail_original',
            field=models.ImageField(default='images/default.png', null=True, upload_to='images/', verbose_name='Thumbnail'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
        migrations.AlterField(
            model_name='venuecontract',
            name='equipment',
            field=models.ManyToManyField(blank=True, to='venues.Equipment', verbose_name='Equipment'),
        ),
        migrations.AlterField(
            model_name='venuecontract',
            name='event',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='venues.Event', verbose_name='Event'),
        ),
        migrations.AlterField(
            model_name='venuecontractprocedure',
            name='venues',
            field=models.ManyToManyField(to='venues.Venue', verbose_name='Venues'),
        ),
    ]
