from django.shortcuts import render
from django.views import View


class TableView(View):
    template_name = 'core/table_view.html'
    header = 'Header'
    request = None

    def get_queryset(self, request):
        raise NotImplementedError()

    def get_table(self):
        raise NotImplementedError()

    def get(self, request):
        queryset = self.get_queryset(request)
        sort = request.GET.get('sort', None)

        if sort:
            queryset.order_by(sort)

        if queryset:
            table = self.get_table()(queryset)
            table.paginate(
                page=request.GET.get('page', 1),
                per_page=request.GET.get('per_page', 25)
            )
        else:
            table = None

        context = {
            'header': self.header,
            'table': table,
        }
        return render(request, self.template_name, context)
