# Generated by Django 3.0.3 on 2020-02-22 19:10

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, null=True)),
                ('slug', models.SlugField(unique=True)),
                ('image', models.ImageField(blank=True, default='images/default.png', null=True, upload_to='images/')),
                ('telephone_private', models.CharField(blank=True, max_length=20, null=True)),
                ('telephone_public', models.CharField(blank=True, max_length=20, null=True)),
                ('email_public', models.EmailField(blank=True, max_length=254, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('info_text', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(blank=True, max_length=50, null=True)),
                ('street_number', models.CharField(blank=True, max_length=10, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=5, null=True)),
                ('city', models.CharField(blank=True, max_length=128, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['postal_code', 'street'],
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_holder', models.CharField(blank=True, max_length=128, null=True)),
                ('iban', models.CharField(blank=True, max_length=40, null=True)),
                ('bic', models.CharField(blank=True, max_length=11, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['bic', 'iban'],
            },
        ),
        migrations.CreateModel(
            name='DeclarationOfIntent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('timestamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('actor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Actor')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('birth_date', models.DateField(null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('core.actor', models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('actor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Actor')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organization_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('core.actor',),
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.CharField(choices=[('p', 'pending'), ('co', 'confirmed'), ('a', 'accepted'), ('f', 'finalized'), ('d', 'disputed'), ('x', 'expired'), ('c', 'canceled')], max_length=2)),
                ('name', models.CharField(max_length=64)),
                ('comment', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('fee_absolute', models.BooleanField(default=False)),
                ('fee_value', models.DecimalField(decimal_places=3, max_digits=13)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Actor')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('p', 'pending'), ('f', 'finalized'), ('fa', 'failed'), ('ca', 'canceled'), ('r', 'refunded')], max_length=2)),
                ('notes', models.TextField(blank=True, null=True, verbose_name='payment notes')),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.PaymentMethod')),
            ],
        ),
        migrations.CreateModel(
            name='GalleryImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='images/')),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Gallery')),
            ],
        ),
        migrations.CreateModel(
            name='ContractTrigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.CharField(choices=[('p', 'pending'), ('co', 'confirmed'), ('a', 'accepted'), ('f', 'finalized'), ('d', 'disputed'), ('x', 'expired'), ('c', 'canceled')], max_length=2)),
                ('name', models.CharField(max_length=64)),
                ('comment', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Actor')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('p', 'pending'), ('co', 'confirmed'), ('a', 'accepted'), ('f', 'finalized'), ('d', 'disputed'), ('x', 'expired'), ('c', 'canceled')], max_length=2)),
                ('acceptance', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contract_acceptance', to='core.DeclarationOfIntent')),
                ('creditor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creditor', to='core.Actor')),
                ('debitor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='debitor', to='core.Actor')),
                ('initiation', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contract_initiation', to='core.DeclarationOfIntent')),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Payment')),
            ],
        ),
        migrations.AddField(
            model_name='actor',
            name='address',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Address'),
        ),
        migrations.AddField(
            model_name='actor',
            name='bank_account',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.BankAccount'),
        ),
        migrations.CreateModel(
            name='OrganizationMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.IntegerField(choices=[(0, 'member'), (1, 'administrator'), (2, 'owner')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('organization', 'user')},
            },
        ),
        migrations.AddField(
            model_name='organization',
            name='members',
            field=models.ManyToManyField(through='core.OrganizationMember', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(blank=True, max_length=128, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('latitude', models.DecimalField(decimal_places=6, default=0, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, default=0, max_digits=9)),
                ('image', models.ImageField(blank=True, default='images/default.png', null=True, upload_to='images/')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Address')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Actor')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='gallery',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='declarationofintent',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bankaccount',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bank_account_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='address',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='address_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
