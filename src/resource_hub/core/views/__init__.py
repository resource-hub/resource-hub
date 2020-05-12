from django.conf import settings
from django.db import transaction
from django.db.models import F, Q
from django.forms import Form
from django.shortcuts import redirect, render, reverse
from django.views import View

from ..forms import BaseFilterForm, TableActionForm


def convert_value(value, field):
    if field.widget.input_type == 'checkbox':
        return True if value == 'on' else False
    return value


class TableView(View):
    template_name = 'core/table_view.html'
    header = 'Header'
    class_ = None
    subclasses = False
    filters = True
    actions = True

    def get_table(self):
        raise NotImplementedError()

    def get_filters(self, request):
        return None

    def get_functions(self, request):
        return None

    def transform_filters(self, filters):
        query = None
        if filters:
            for filter_, content in filters.items():
                parameter = {filter_: content['value']}
                if query:
                    query.add(Q(**parameter), content['connector'])
                else:
                    query = Q(**parameter, _connector=content['connector'])
        return query

    def append_functions(self, queryset, functions, query):
        if functions:
            for name, content in functions.items():
                if name == 'annotate':
                    queryset.filter(query).annotate(
                        *content['args'], **content['kwargs'])
        return queryset

    def get_queryset(self, request):
        sort = request.GET.get('sort', None)
        form = self.get_filter_form(request, request.GET)
        query = self.transform_filters(self.get_filters(request))
        if 'is_deleted' not in request.GET:
            query.add(Q(is_deleted=False), Q.AND)
        for name, field in form.fields.items():
            if name != 'per_page':
                value = convert_value(request.GET.get(name, None), field)
                if value:
                    parameter = {name: value}
                    if query:
                        query.add(Q(**parameter), Q.AND)
                    else:
                        query = Q(**parameter)
        queryset = self.class_.all_objects
        if self.subclasses:
            queryset = queryset.select_subclasses()
        if sort:
            return queryset.filter(query).order_by(sort)
        return queryset.filter(query)

    def get_action_form(self, request):
        if not self.actions:
            return Form()
        return TableActionForm()

    def get_filter_form(self, request, data):
        if not self.filters:
            return Form()
        if data:
            return BaseFilterForm(data)
        return BaseFilterForm()

    def get_context(self, request):
        queryset = self.get_queryset(request)

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

    def render(self, request):
        return render(request, self.template_name, self.get_context(request))

    def get(self, request):
        return self.render(request)

    def post(self, request):
        action = request.POST.get('action', None)
        selected_rows = request.POST.getlist('select[]')
        if self.class_:
            with transaction.atomic():
                if action == 'trash':
                    self.class_.objects.filter(
                        pk__in=selected_rows).soft_delete()
                if action == 'untrash':
                    self.class_.all_objects.filter(
                        pk__in=selected_rows).update(is_deleted=False)
        return redirect(reverse('{}:{}'.format(request.resolver_match.namespace, request.resolver_match.url_name)), kwargs=request.resolver_match.kwargs)
