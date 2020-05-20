# Generated by Django 3.0.5 on 2020-05-13 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='donation',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='original_owner',
            field=models.CharField(blank=True, help_text='Which entity bought or donated the item?', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='thumbnail_original',
            field=models.ImageField(upload_to='images/', verbose_name='thumbnail'),
        ),
    ]