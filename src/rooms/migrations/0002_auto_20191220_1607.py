# Generated by Django 3.0 on 2019-12-20 16:07

from django.db import migrations
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(default='test'),
            preserve_default=False,
        ),
    ]