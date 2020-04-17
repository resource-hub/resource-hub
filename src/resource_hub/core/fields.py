import bleach
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import DecimalField

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
