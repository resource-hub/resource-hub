# Generated by Django 3.0.4 on 2020-04-14 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20200414_2008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoiceposition',
            name='event_date_from',
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_from',
            field=models.TextField(null=True),
        ),
    ]