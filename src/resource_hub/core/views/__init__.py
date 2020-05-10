from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.forms import Form
from django.shortcuts import redirect, render, reverse
from django.views import View

from ..forms import TableActionForm


class TableView(View):
    template_name = 'core/table_view.html'
    header = 'Header'
    class_ = None

    def get_queryset(self, request, sort, filters):
        raise NotImplementedError()

    def get_table(self):
        raise NotImplementedError()

    def get_action_form(self, request):
        return TableActionForm()

    def get_filter_form(self, request, data):
        if data:
            return Form(data)
        return Form()

    def get_context(self, request):
        sort = request.GET.get('sort', None)
        filters = self.get_filters(request)
        queryset = self.get_queryset(request, sort, filters=filters)

        if queryset:
            table = self.get_table()(queryset)
            table.paginate(
                page=request.GET.get('page', 1),
                per_page=request.GET.get('per_page', settings.DEFAULT_PER_PAGE)
            )
        else:
            table = None
        return {
            'header': self.header,
            'table': table,
            'filter_form': self.get_filter_form(request, request.GET),
            'action_form': self.get_action_form(request),
        }

    def get_filters(self, request):
        form = self.get_filter_form(request, request.GET)
        query = None
        for field in form.fields:
            if field != 'per_page':
                value = request.GET.get(field, None)
                if value:
                    parameter = {field: value}
                    if query:
                        query.add(Q(**parameter), Q.AND)
                    else:
                        query = Q(**parameter)
        return query

    def render(self, request):
        return render(request, self.template_name, self.get_context(request))

    def get(self, request):
        return self.render(request)

    def post(self, request):
        action = request.POST.get('action', None)
        selected_rows = request.POST.getlist('select[]')
        with transaction.atomic():
            if action == 'trash' and self.class_:
                self.class_.objects.filter(pk__in=selected_rows).soft_delete()
        return redirect(reverse('{}:{}'.format(request.resolver_match.namespace, request.resolver_match.url_name)), kwargs=request.resolver_match.kwargs)
