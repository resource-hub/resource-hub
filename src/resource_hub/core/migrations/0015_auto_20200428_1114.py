# Generated by Django 3.0.5 on 2020-04-28 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20200428_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractprocedure',
            name='notes',
            field=models.TextField(blank=True, help_text='This text will be added to the notification when a contract starts running', null=True, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='typ',
            field=models.CharField(choices=[('info circle', 'info'), ('bolt', 'action'), ('handshake', 'contract'), ('file alternate outline', 'monetary')], max_length=30),
        ),
    ]
