from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from resource_hub.core.forms import ActorForm, ReportBugForm
from resource_hub.core.models import Actor, Location

from ..utils import get_site_info


def index(request):
    return redirect(reverse('core:home'))


class Home(View):
    def get(self, request):
        return render(request, 'core/home.html')


class Terms(View):
    def get(self, request):
        return render(request, 'core/terms_and_conditions.html', get_site_info())


class DataPrivacyStatement(View):
    def get(self, request):
        return render(request, 'core/data_privacy_statement.html', get_site_info())


class Imprint(View):
    def get(self, request):
        return render(request, 'core/imprint.html', get_site_info())


class ReportBug(View):
    template_name = 'core/report_bug.html'
    context = {
        'bug_form': ReportBugForm(),
    }

    def get(self, request):
        return render(request, self.template_name, self.context)

    def post(self, request):
        bug_form = ReportBugForm(request.POST)

        if bug_form.is_valid():
            bug_form.post()
            message = _('Your issue has been posted!')
            messages.add_message(request, messages.SUCCESS, message)

            return redirect(reverse('core:report_bug'))

        self.context['bug_form'] = bug_form
        return render(request, self.template_name, self.context)


class Language(View):
    def get(self, request):
        return render(request, 'core/language.html')


class ActorProfile(View):
    def get(self, request, slug):
        actor = get_object_or_404(Actor, slug=slug)
        context = {
            'actor': actor,
        }
        return render(request, 'core/actor_profile.html', context)


class LocationsProfile(View):
    def get(self, request, slug):
        location = get_object_or_404(Location, slug=slug)
        context = {
            'location': location
        }
        return render(request, 'core/locations_profile.html', context)
