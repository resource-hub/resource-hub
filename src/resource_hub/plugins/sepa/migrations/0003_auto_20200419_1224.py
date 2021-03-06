# Generated by Django 3.0.5 on 2020-04-19 12:24

from django.db import migrations
import resource_hub.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sepa', '0002_auto_20200418_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sepadirectdebitpayment',
            name='currency',
            field=resource_hub.core.fields.CurrencyField(choices=[('EUR', 'Euro (EUR)')], default='EUR', max_length=3, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='sepadirectdebitxml',
            name='currency',
            field=resource_hub.core.fields.CurrencyField(choices=[('EUR', 'Euro (EUR)')], default='EUR', max_length=3, verbose_name='Currency'),
        ),
    ]
