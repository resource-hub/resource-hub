# Generated by Django 3.0.5 on 2020-05-23 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0008_auto_20200522_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='custom_id',
            field=models.CharField(blank=True, db_index=True, help_text='ID field for bardcodes etc.', max_length=100, null=True, verbose_name='Custom ID'),
        ),
        migrations.AlterField(
            model_name='itemcontract',
            name='note',
            field=models.TextField(blank=True, help_text='This message will be sent to the owner. This allows to negiotate pickup times etc.', null=True, verbose_name='Note'),
        ),
    ]
