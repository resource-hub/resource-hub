from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Address(models.Model):
    """ describe address """

    # Fields
    street = models.CharField(max_length=50, null=True, blank=True)
    street_number = models.CharField(max_length=10, null=True, blank=True)
    postal_code = models.CharField(max_length=5, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name='address_created_by',
        null=True,
        on_delete=models.SET_NULL
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        null=True,
        related_name='address_updated_by',
        on_delete=models.SET_NULL
    )

    # Metadata
    class Meta:
        ordering = ['postal_code', 'street']

    # Methods
    def __str__(self):
        return '{} {} in {} {}'.format(
            self.street,
            self.street_number,
            self.postal_code,
            self.city
        )


class BankAccount(models.Model):
    """ describes a bank account """

    # Fields
    account_holder = models.CharField(max_length=100, null=True, blank=True)
    iban = models.CharField(max_length=40, null=True, blank=True)
    bic = models.CharField(max_length=11, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name='bank_account_created_by',
        null=True,
        on_delete=models.SET_NULL
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        null=True,
        related_name='bank_account_updated_by',
        on_delete=models.SET_NULL
    )

    # Metadata

    class Meta:
        ordering = ['bic', 'iban']

    # Methods
    def __str__(self):
        return '{} with account {} at {}'.format(
            self.account_holder,
            self.iban,
            self.bic
        )


class Info(models.Model):
    """ entity specific information """

    # Fields
    address = models.OneToOneField(
        Address,
        null=True,
        on_delete=models.SET_NULL
    )
    bank_account = models.OneToOneField(
        BankAccount,
        null=True,
        on_delete=models.SET_NULL
    )
    image = models.ImageField(null=True, blank=True)
    telephone_private = models.CharField(max_length=20, null=True, blank=True)
    telephone_public = models.CharField(max_length=20, null=True, blank=True)
    email_public = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    info_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name='info_created_by',
        null=True,
        on_delete=models.SET_NULL
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        null=True,
        related_name='info_updated_by',
        on_delete=models.SET_NULL
    )

    # Metadata
    class Meta:
        ordering = ['id']

    # Methods
    def __str__(self):
        return 'Info'


class Location(models.Model):
    """ describing locations """

    # Fields
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name='location_created_by',
        null=True,
        on_delete=models.SET_NULL
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        null=True,
        related_name='location_updated_by',
        on_delete=models.SET_NULL
    )

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name


class Person(models.Model):
    """ natural person """

    # Fields
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    info = models.OneToOneField(
        Info,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    birth_date = models.DateField()


class Organization(models.Model):
    """ juristic person"""

    # Fields
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE
    )
    info = models.OneToOneField(
        Info,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
