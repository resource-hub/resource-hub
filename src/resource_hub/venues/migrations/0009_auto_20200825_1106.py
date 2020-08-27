# Generated by Django 3.0.9 on 2020-08-25 11:06

from django.db import migrations, models
import resource_hub.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0008_auto_20200825_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='usage',
            field=resource_hub.core.fields.MultipleChoiceArrayField(base_field=models.CharField(choices=[('o', 'other'), ('w', 'workshop')], default='o', max_length=3, verbose_name='Usage type'), default=['o'], size=None),
        ),
    ]