# Generated by Django 2.2.4 on 2019-09-18 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190917_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='image',
            field=models.ImageField(blank=True, default='static/logo.png', null=True, upload_to='images/'),
        ),
    ]
