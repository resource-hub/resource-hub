from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Actor(models.Model):
    """ existing combinations of users and organizations """

    # Fields
    name = models.CharField(max_length=128, null=True)
    address = models.OneToOneField(
        'Address',
        null=True,
        on_delete=models.SET_NULL
    )
    bank_account = models.OneToOneField(
        'BankAccount',
        null=True,
        on_delete=models.SET_NULL
    )
    image = models.ImageField(null=True, blank=True,
                              upload_to='images/', default='images/default.png')
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(100, 100)],
        format='PNG',
        options={'quality': 60}
    )
    thumbnail_small = ImageSpecField(
        source='image',
        processors=[ResizeToFill(40, 40)],
        format='PNG',
        options={'quality': 60}
    )
    thumbnail_large = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='PNG',
        options={'quality': 90}
    )
    telephone_private = models.CharField(max_length=20, null=True, blank=True)
    telephone_public = models.CharField(max_length=20, null=True, blank=True)
    email_public = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    info_text = models.TextField(null=True, blank=True)

    # Metadata
    class Meta:
        ordering = ['id']

    # Methods
    def __str__(self):
        return str(self.name)


class User(AbstractUser, Actor):
    """ natural person """
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True)


class Address(models.Model):
    """ describe address """

    # Fields
    street = models.CharField(max_length=50, null=True, blank=True)
    street_number = models.CharField(max_length=10, null=True, blank=True)
    postal_code = models.CharField(max_length=5, null=True, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
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
    account_holder = models.CharField(max_length=128, null=True, blank=True)
    iban = models.CharField(max_length=40, null=True, blank=True)
    bic = models.CharField(max_length=11, null=True, blank=True)
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


class Location(models.Model):
    """ describing locations """

    # Fields
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    image = models.ImageField(null=True, blank=True,
                              upload_to='images/', default='images/default.png')
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 300)],
        format='PNG',
        options={'quality': 60}
    )
    owner = models.ForeignKey(Actor, on_delete=models.CASCADE)
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


class Organization(Actor):
    """ juristic person"""

    # fields
    members = models.ManyToManyField(User, through='OrganizationMember')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        related_name='organization_created_by',
        null=True,
        on_delete=models.SET_NULL
    )

    # Methods
    def __str__(self):
        return super().name


class OrganizationMember(models.Model):
    """ member of organization """

    # model constants
    MEMBER = 0
    ADMIN = 1
    OWNER = 2

    ORGANIZATION_ROLES = [
        (MEMBER, _('Member')),
        (ADMIN, _('Administrator')),
        (OWNER, _('Owner')),
    ]

    # fields
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(
        choices=ORGANIZATION_ROLES,
        default=MEMBER,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'user',)

    def is_admin(self):
        if self.role == OrganizationMember.ADMIN or self.role == OrganizationMember.OWNER:
            return True
        else:
            return False

    @classmethod
    def get_role(user, organization):
        role = OrganizationMember.objects.get(
            organization=organization,
            user=user
        ).get_role_display()
        return role


class Gallery(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)


class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    image = models.ImageField(null=False, blank=True,
                              upload_to='images/')
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 70}
    )
