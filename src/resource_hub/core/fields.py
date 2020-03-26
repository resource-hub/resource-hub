import bleach
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import DecimalField

from django_summernote.widgets import SummernoteWidget

#
# form fields
#
ALLOWED_TAGS = [
    'a', 'div', 'p', 'span', 'img', 'em', 'i', 'li', 'ol', 'ul', 'strong', 'br',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'tbody', 'thead', 'tr', 'td',
    'abbr', 'acronym', 'b', 'blockquote', 'code', 'strike', 'u', 'sup', 'sub',
]

STYLES = [
    'background-color', 'font-size', 'line-height', 'color', 'font-family'
]

ATTRIBUTES = {
    '*': ['style', 'align', 'title', ],
    'a': ['href', ],
}


class HTMLField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(HTMLField, self).__init__(*args, **kwargs)
        self.widget = SummernoteWidget()

    def to_python(self, value):
        value = super(HTMLField, self).to_python(value)
        return bleach.clean(
            value, tags=ALLOWED_TAGS, attributes=ATTRIBUTES, styles=STYLES)


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
