import bleach
from django import forms
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CharField, DecimalField
from django.utils.translation import gettext_lazy as _

from django_summernote.fields import SummernoteTextFormField


class HTMLField(SummernoteTextFormField):
    pass

#
# model fields
#


class PercentField(DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = 0
        kwargs['max_digits'] = 6
        kwargs['decimal_places'] = 3
        kwargs['validators'] = [
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
        super().__init__(*args, **kwargs)


class CurrencyField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 3
        kwargs['choices'] = settings.CURRENCIES
        kwargs['verbose_name'] = _('Currency')
        kwargs['default'] = settings.CURRENCIES[0][0]
        super().__init__(*args, **kwargs)
