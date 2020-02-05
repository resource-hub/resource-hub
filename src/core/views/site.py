from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View

from core.forms import ReportIssueForm, ActorForm


def index(request):
    return redirect(reverse('core:home'))


class Home(View):
    def get(self, request):
        context = {'userform': ActorForm()}
        return render(request, 'core/home.html', context)


class Terms(View):
    def get(self, request):
        return render(request, 'core/terms_and_conditions.html')


class Support(View):
    template_name = 'core/support.html'
    context = {
        'issue_form': ReportIssueForm(),
    }

    def get(self, request):
        return render(request, self.template_name, self.context)

    def post(self, request):
        issue_form = ReportIssueForm(request.POST)

        if issue_form.is_valid():
            try:
                issue_form.post()
                message = _('Your issue has been posted!')
                messages.add_message(request, messages.SUCCESS, message)
            except IOError:
                message = _('Your issue could not be posted!')
                messages.add_message(request, messages.ERROR, message)
                self.context['issue_form'] = issue_form
                return render(request, self.template_name, self.context)

            return redirect(reverse('core:support'))

        self.context['issue_form'] = issue_form
        return render(request, self.template_name, self.context)


class Language(View):
    def get(self, request):
        return render(request, 'core/language.html')
