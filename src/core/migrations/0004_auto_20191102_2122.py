# Generated by Django 2.2.4 on 2019-11-02 21:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_user_name_public'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='organizationmember',
            unique_together={('organization', 'user')},
        ),
    ]