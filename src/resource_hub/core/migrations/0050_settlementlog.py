# Generated by Django 3.0.5 on 2020-04-16 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20200416_0005'),
    ]

    operations = [
        migrations.CreateModel(
            name='SettlementLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settlement_logs', to='core.Contract')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]