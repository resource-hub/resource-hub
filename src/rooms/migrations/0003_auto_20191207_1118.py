# Generated by Django 3.0 on 2019-12-07 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_auto_20191205_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(to='rooms.EventTag'),
        ),
    ]