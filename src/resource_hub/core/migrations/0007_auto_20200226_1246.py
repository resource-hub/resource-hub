# Generated by Django 3.0.3 on 2020-02-26 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200226_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='declarationofintent',
            name='ip_routable',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='state',
            field=models.CharField(choices=[('p', 'pending'), ('w', 'waiting'), ('r', 'running'), ('d', 'disputing'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled')], max_length=2),
        ),
        migrations.AlterField(
            model_name='contracttrigger',
            name='condition',
            field=models.CharField(choices=[('p', 'pending'), ('w', 'waiting'), ('r', 'running'), ('d', 'disputing'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled')], max_length=2),
        ),
        migrations.AlterField(
            model_name='declarationofintent',
            name='ip',
            field=models.GenericIPAddressField(null=True),
        ),
        migrations.AlterField(
            model_name='declarationofintent',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='condition',
            field=models.CharField(choices=[('p', 'pending'), ('w', 'waiting'), ('r', 'running'), ('d', 'disputing'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled')], max_length=2),
        ),
    ]
