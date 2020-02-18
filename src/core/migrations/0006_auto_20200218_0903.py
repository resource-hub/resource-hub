# Generated by Django 3.0.3 on 2020-02-18 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200212_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='contracttrigger',
            name='condition',
            field=models.CharField(choices=[('p', 'pending'), ('co', 'confirmed'), ('a', 'accepted'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled')], default='p', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='condition',
            field=models.CharField(choices=[('p', 'pending'), ('co', 'confirmed'), ('a', 'accepted'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled')], default='p', max_length=2),
            preserve_default=False,
        ),
    ]
