from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class User(AbstractUser):
    """ natural person """
    email = models.EmailField(unique=True)
    birth_date = models.DateField()
    info = models.OneToOneField(
        'Info',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Role:
        USER = 'usr'
        ORGANIZATION = 'org'

        def is_user(request):
            return request.session['role'] == USER


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
    image = models.ImageField(null=True, blank=True,
                              upload_to='images/')
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
    telephone_private = models.CharField(max_length=20, null=True, blank=True)
    telephone_public = models.CharField(max_length=20, null=True, blank=True)
    email_public = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    info_text = models.TextField(null=True, blank=True)
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
    name = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
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


class Organization(models.Model):
    """ juristic person"""

    # fields
    name = models.CharField(max_length=128, unique=True, null=False)
    info = models.OneToOneField(
        Info,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
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
        return self.name


class OrganizationMember(models.Model):
    """ member of organization """

    # model constants
    MEMBER = 'mem'
    ADMIN = 'adm'
    OWNER = 'own'

    ORGANIZATION_ROLES = [
        (MEMBER, _('Member')),
        (ADMIN, _('Administrator')),
        (OWNER, _('Owner')),
    ]

    # fields
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=3,
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

    def get_role(user, organization):
        role = OrganizationMember.objects.get(
            organization=organization,
            user=user
        ).get_role_display()
        return role


class Actor(models.Model):
    """ existing combinations of users and organizations """

    # fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('user', 'organization',)
