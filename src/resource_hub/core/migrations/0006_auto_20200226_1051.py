# Generated by Django 3.0.3 on 2020-02-26 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200224_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='fee_value',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=13),
        ),
    ]