# Generated by Django 3.1 on 2020-10-04 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20200930_0845'),
        ('items', '0012_remove_item_attachment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itemprice',
            old_name='item',
            new_name='item_ptr',
        ),
        migrations.AlterField(
            model_name='item',
            name='base_price',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.price', verbose_name='Base price'),
        ),
        migrations.AlterField(
            model_name='item',
            name='contract_procedure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.contractprocedure', verbose_name='Contract procedure'),
        ),
        migrations.AlterField(
            model_name='item',
            name='location',
            field=models.ForeignKey(help_text="All public and current role's locations", on_delete=django.db.models.deletion.CASCADE, to='core.location', verbose_name='Location'),
        ),
    ]
