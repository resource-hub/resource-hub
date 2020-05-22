# Generated by Django 3.0.5 on 2020-05-22 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sepa', '0005_auto_20200428_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sepadirectdebitxml',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='sepadirectdebitxml',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Deleted?'),
        ),
        migrations.AlterField(
            model_name='sepadirectdebitxml',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
    ]
