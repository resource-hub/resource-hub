# Generated by Django 3.0.4 on 2020-03-22 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20200316_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='addressee',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Actor'),
        ),
    ]