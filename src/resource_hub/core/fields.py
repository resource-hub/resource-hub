import bleach
from django import forms
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CharField, DecimalField
from django.forms import MultipleChoiceField
from django.utils.translation import gettext_lazy as _

from django_summernote.fields import SummernoteTextFormField


# form fields
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


class CustomMultipleChoiceField(MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(CustomMultipleChoiceField, self).__init__(*args, **kwargs)
        self.widget.attrs.update({'class': 'ui fluid normal dropdown'})

# model fields


class HTMLField(SummernoteTextFormField):
    pass


class MultipleChoiceArrayField(ArrayField):
    ''' thanks to: https://stackoverflow.com/a/39833588/12653439 '''

    def formfield(self, **kwargs):
        defaults = {
            'form_class': CustomMultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)

    def to_python(self, value):
        ''' allow for usage with IntegerField: https://gist.github.com/danni/f55c4ce19598b2b345ef#gistcomment-2789863 '''
        res = super().to_python(value)
        if isinstance(res, list):
            value = [self.base_field.to_python(val) for val in res]
        return value
