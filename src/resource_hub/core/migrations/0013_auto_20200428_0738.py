# Generated by Django 3.0.5 on 2020-04-28 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20200427_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.CharField(choices=[('c', 'created'), ('b', 'booked'), ('co', 'confirmed'), ('a', 'accepted')], max_length=3),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.TextField(null=True),
        ),
    ]
