# Generated by Django 3.0.9 on 2020-09-24 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_icsfile'),
        ('sepa', '0006_auto_20200522_1209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sepadirectdebitxml',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='sepadirectdebitxml',
            name='file',
        ),
        migrations.RemoveField(
            model_name='sepadirectdebitxml',
            name='id',
        ),
        migrations.RemoveField(
            model_name='sepadirectdebitxml',
            name='is_deleted',
        ),
        migrations.RemoveField(
            model_name='sepadirectdebitxml',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='sepadirectdebitxml',
            name='file_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.File'),
            preserve_default=False,
        ),
    ]
