# Generated by Django 3.0.3 on 2020-02-10 22:37

import core.models
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200206_2118'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('p', 'pending'), ('a', 'accepted'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('absolute', models.BooleanField(default=False)),
                ('value', models.DecimalField(decimal_places=3, max_digits=13)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(db_index=True, max_length=160)),
                ('invoice_no', models.CharField(db_index=True, max_length=19)),
                ('full_invoice_no', models.CharField(db_index=True, max_length=190)),
                ('is_cancellation', models.BooleanField(default=False)),
                ('invoice_from', models.TextField()),
                ('invoice_from_name', models.CharField(max_length=190, null=True)),
                ('invoice_from_zipcode', models.CharField(max_length=190, null=True)),
                ('invoice_from_city', models.CharField(max_length=190, null=True)),
                ('invoice_from_country', django_countries.fields.CountryField(max_length=2, null=True)),
                ('invoice_from_tax_id', models.CharField(max_length=190, null=True)),
                ('invoice_from_vat_id', models.CharField(max_length=190, null=True)),
                ('invoice_to', models.TextField()),
                ('invoice_to_company', models.TextField(null=True)),
                ('invoice_to_name', models.TextField(null=True)),
                ('invoice_to_street', models.TextField(null=True)),
                ('invoice_to_zipcode', models.CharField(max_length=190, null=True)),
                ('invoice_to_city', models.TextField(null=True)),
                ('invoice_to_state', models.CharField(max_length=190, null=True)),
                ('invoice_to_country', django_countries.fields.CountryField(max_length=2, null=True)),
                ('invoice_to_vat_id', models.TextField(null=True)),
                ('invoice_to_beneficiary', models.TextField(null=True)),
                ('date', models.DateField(default=core.models.today)),
                ('locale', models.CharField(default='en', max_length=50)),
                ('introductory_text', models.TextField(blank=True)),
                ('additional_text', models.TextField(blank=True)),
                ('reverse_charge', models.BooleanField(default=False)),
                ('payment_provider_text', models.TextField(blank=True)),
                ('footer_text', models.TextField(blank=True)),
                ('foreign_currency_display', models.CharField(blank=True, max_length=50, null=True)),
                ('foreign_currency_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('foreign_currency_rate_date', models.DateField(blank=True, null=True)),
                ('shredded', models.BooleanField(default=False)),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=core.models.invoice_filename)),
                ('internal_reference', models.TextField(blank=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Contract')),
                ('refers', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='refered', to='core.Invoice')),
            ],
        ),
        migrations.AlterField(
            model_name='organizationmember',
            name='role',
            field=models.IntegerField(choices=[(0, 'member'), (1, 'administrator'), (2, 'owner')], default=0),
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('function_call', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=64)),
                ('comment', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('fee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Fee')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Actor')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('p', 'pending'), ('f', 'finalized'), ('fa', 'failed'), ('ca', 'canceled'), ('r', 'refunded')], max_length=2)),
                ('notes', models.TextField(blank=True, null=True, verbose_name='payment notes')),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.PaymentMethod')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(default=0)),
                ('description', models.TextField()),
                ('gross_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax_value', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=7)),
                ('tax_name', models.CharField(max_length=190)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='core.Invoice')),
            ],
            options={
                'ordering': ('position', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='DeclarationOfIntent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('timestamp', models.DateTimeField()),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContractTrigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('function_call', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=64)),
                ('comment', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('provider', models.CharField(max_length=64)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Actor')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='contract',
            name='acceptance',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='acceptance', to='core.DeclarationOfIntent'),
        ),
        migrations.AddField(
            model_name='contract',
            name='creditor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creditor', to='core.Actor'),
        ),
        migrations.AddField(
            model_name='contract',
            name='debitor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='debitor', to='core.Actor'),
        ),
        migrations.AddField(
            model_name='contract',
            name='initiation',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='initiation', to='core.DeclarationOfIntent'),
        ),
        migrations.AddField(
            model_name='contract',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Payment'),
        ),
    ]