from django.shortcuts import render
from django.views import View


class TableView(View):
    template_name = 'core/table_view.html'
    header = 'Header'
    request = None

    def get_queryset(self):
        raise NotImplementedError()

    def get_table(self):
        raise NotImplementedError()

    def get(self, request):
        self.request = request
        queryset = self.get_queryset()

        if queryset:
            table = self.get_table()(queryset)
        else:
            table = None

        context = {
            'header': self.header,
            'table': table,
        }
        return render(request, self.template_name, context)
