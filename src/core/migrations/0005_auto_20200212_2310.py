# Generated by Django 3.0.3 on 2020-02-12 23:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200210_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='acceptance',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contract_acceptance', to='core.DeclarationOfIntent'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='initiation',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contract_initiation', to='core.DeclarationOfIntent'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='state',
            field=models.CharField(choices=[('p', 'pending'), ('co', 'confirmed'), ('a', 'accepted'), ('f', 'finalized'), ('x', 'expired'), ('c', 'canceled')], max_length=2),
        ),
    ]