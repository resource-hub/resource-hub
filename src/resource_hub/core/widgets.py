from django.forms.renderers import TemplatesSetting
from django.forms.widgets import CheckboxInput, TextInput, TimeInput
from django.template.context import make_context


class UISearchField(TextInput):
    template_name = 'core/widgets/search_field.html'


class UICheckboxSlider(CheckboxInput):
    template_name = 'core/widgets/checkbox_slider.html'


class TimeInputCustom(TimeInput):
    template_name = 'core/widgets/time_input.html'


class IBANInput(TextInput):
    template_name = 'core/widgets/iban_input.html'
