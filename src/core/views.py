from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from core.forms import *


def index(request):
    return render(request, 'core/index.html')


def register(request):
    if request.method == 'POST':
        user_base_form = UserBaseForm(request.POST)
        person_form = PersonForm(request.POST)
        info_form = InfoForm(request.POST)
        address_form = AddressForm(request.POST)
        bank_account_form = BankAccountForm(request.POST)

        if user_base_form.is_valid and person_form.is_valid and info_form.is_valid and address_form.is_valid:
            user_base_form.save()
            person_form.save(commit=false)
            person_form.user_id = user_base_form
            person_form.save()
            username = user_base_form.cleaned_data.get('username')
            raw_password = user_base_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/profile')
    else:
        if request.user.is_authenticated:
            return redirect('/profile')
        else:
            user_base_form = UserBaseForm()
            person_form = PersonForm()
            info_form = InfoForm()
            address_form = AddressForm()
            bank_account_form = BankAccountForm()

    context = {
        'user_base_form': user_base_form,
        'person_form': person_form,
        'info_form': info_form,
        'address_form': address_form,
        'bank_account_form': bank_account_form,
    }

    return render(request, 'core/account/register.html', context)


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('/profile')
    else:
        return LoginView.as_view(
            template_name='core/account/login.html')(request)


def profile(request):
    return render(request, 'core/account/profile.html')
