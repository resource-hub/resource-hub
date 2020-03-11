# Generated by Django 3.0.3 on 2020-03-01 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200228_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=5, max_digits=15)),
                ('currency', models.CharField(default='EUR', max_length=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('addressee', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Actor')),
            ],
        ),
        migrations.AddField(
            model_name='contract',
            name='price',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.Price'),
        ),
    ]