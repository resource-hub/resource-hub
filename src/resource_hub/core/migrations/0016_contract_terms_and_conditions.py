# Generated by Django 3.0.5 on 2020-04-28 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20200428_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='terms_and_conditions',
            field=models.TextField(null=True),
        ),
    ]