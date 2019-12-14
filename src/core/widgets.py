from django.forms.widgets import TextInput


class UISearchField(TextInput):
    template_name = 'core/ui_search_widget.html'
