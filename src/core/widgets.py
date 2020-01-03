from django.forms.widgets import TextInput, CheckboxInput, TimeInput


class UISearchField(TextInput):
    template_name = 'core/widgets/search_field.html'


class UICheckboxSlider(CheckboxInput):
    template_name = 'core/widgets/checkbox_slider.html'


class TimeInput(TimeInput):
    template_name = 'core/widgets/time_input.html'
