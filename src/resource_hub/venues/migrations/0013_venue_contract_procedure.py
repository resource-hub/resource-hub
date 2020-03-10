# Generated by Django 3.0.4 on 2020-03-08 20:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20200308_2033'),
        ('venues', '0012_auto_20200307_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='contract_procedure',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.ContractProcedure'),
        ),
    ]
