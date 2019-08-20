from django.contrib.postgres.fields import HStoreField
from django.db import models

# Create your models here.


class Address(models.Model):
    street = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)
    postal_code = models.CharField(max_length=5)
    city = models.CharField(max_length=100)


class Bank_Account(models.Model):
    account_holder = models.CharField(max_length=100)
    iban = models.CharField(max_length=40)
    bic = models.CharField(max_length=11)


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    rights = models.SmallIntegerField()
    address_id = models.ForeignKey(
        Address, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class Location(models.Model):
    address_id = models.ForeignKey(Address, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
