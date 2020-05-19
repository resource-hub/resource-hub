# Generated by Django 3.0.5 on 2020-05-18 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20200511_1045'),
        ('items', '0002_auto_20200513_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('v', 'vehicles'), ('t', 'tools'), ('e', 'electronics'), ('p', 'photography'), ('vi', 'video'), ('o', 'other')], default='o', max_length=3),
        ),
        migrations.AlterField(
            model_name='item',
            name='instructions',
            field=models.TextField(blank=True, help_text='These instructions will be included in the confirmation mail text', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='self_pickup',
            field=models.CharField(choices=[('n', 'not allowed'), ('l', 'limited'), ('a', 'allowed')], default='n', max_length=2),
        ),
        migrations.AlterField(
            model_name='item',
            name='unit',
            field=models.CharField(choices=[('h', 'hours'), ('d', 'days')], default='d', max_length=3),
        ),
        migrations.AlterField(
            model_name='itemcontractprocedure',
            name='self_pickup_group',
            field=models.ManyToManyField(blank=True, help_text="The group granted self pickup if item's self pickup is limited", to='core.Actor'),
        ),
    ]
