# Generated by Django 3.0.5 on 2020-04-18 00:43

from django.db import migrations, models
import resource_hub.plugins.sepa.models


class Migration(migrations.Migration):

    dependencies = [
        ('sepa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sepadirectdebitxml',
            name='file',
            field=models.FileField(upload_to=resource_hub.plugins.sepa.models.sepaxml_filename),
        ),
    ]
