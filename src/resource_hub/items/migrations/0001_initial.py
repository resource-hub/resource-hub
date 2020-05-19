# Generated by Django 3.0.5 on 2020-05-13 12:04

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0028_auto_20200511_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(default='p', max_length=2)),
                ('state_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='state')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('custom_id', models.CharField(blank=True, help_text='ID field for bardcodes etc.', max_length=100, null=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('manufacturer', models.CharField(blank=True, max_length=64, null=True)),
                ('model', models.CharField(blank=True, max_length=64, null=True)),
                ('serial_no', models.CharField(blank=True, max_length=128, null=True)),
                ('location_code', models.CharField(blank=True, max_length=255, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('unit', models.CharField(choices=[('h', 'hours'), ('d', 'days')], max_length=3)),
                ('maximum_duration', models.IntegerField(default=0, help_text='Maximimum duration the item can be lent. Value of 0 means unlimited.')),
                ('self_pickup', models.CharField(choices=[('n', 'not allowed'), ('l', 'limited'), ('a', 'allowed')], max_length=2)),
                ('damages', models.TextField(blank=True, null=True)),
                ('category', models.CharField(choices=[('v', 'vehicles'), ('t', 'tools'), ('e', 'electronics'), ('p', 'photography'), ('vi', 'video')], max_length=3)),
                ('instructions', models.TextField(help_text='These instructions will be included in the confirmation mail text')),
                ('attachment', models.FileField(blank=True, help_text='This file will be attached to the confirmation mail', null=True, upload_to='')),
                ('thumbnail_original', models.ImageField(upload_to='images/')),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('base_price', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='item_base_price', to='core.Price')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('dtstart', models.DateTimeField()),
                ('dtend', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemPrice',
            fields=[
                ('price_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Price')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prices', to='items.Item')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.price',),
        ),
        migrations.CreateModel(
            name='ItemContractProcedure',
            fields=[
                ('contractprocedure_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ContractProcedure')),
                ('self_pickup_group', models.ManyToManyField(to='core.Actor')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.contractprocedure',),
        ),
        migrations.CreateModel(
            name='ItemContract',
            fields=[
                ('contract_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Contract')),
                ('items', models.ManyToManyField(related_name='contracts', through='items.ItemBooking', to='items.Item')),
            ],
            options={
                'abstract': False,
            },
            bases=('core.contract',),
        ),
        migrations.AddField(
            model_name='itembooking',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='items.ItemContract'),
        ),
        migrations.AddField(
            model_name='itembooking',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='items.Item'),
        ),
        migrations.AddField(
            model_name='item',
            name='contract_procedure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='items.ItemContractProcedure'),
        ),
        migrations.AddField(
            model_name='item',
            name='gallery',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Gallery'),
        ),
        migrations.AddField(
            model_name='item',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.Location'),
        ),
        migrations.AddField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.Actor'),
        ),
        migrations.AddField(
            model_name='item',
            name='purchase_price',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_purchase_price', to='core.Price'),
        ),
        migrations.AddField(
            model_name='item',
            name='replacement_price',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_replacement_price', to='core.Price'),
        ),
    ]
