# Generated by Django 3.0.5 on 2020-04-25 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20200425_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractprocedure',
            name='auto_accept',
            field=models.BooleanField(default=False, help_text='Automatically accept the booking?'),
        ),
        migrations.AlterField(
            model_name='contractprocedure',
            name='name',
            field=models.CharField(help_text='Give the procedure a name so you can identify it easier', max_length=64),
        ),
        migrations.AlterField(
            model_name='contractprocedure',
            name='payment_methods',
            field=models.ManyToManyField(help_text='Choose the payment methods you want to use for this venue', to='core.PaymentMethod'),
        ),
    ]
