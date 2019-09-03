from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse
from core.forms import *
from core.models import *


def index(request):
    return render(request, 'core/index.html')


def register(request):
    if request.method == 'POST':
        user_form = UserBaseForm(request.POST)
        info_form = InfoForm(request.POST)
        address_form = AddressForm(request.POST)
        bank_account_form = BankAccountForm(request.POST)

        if (user_form.is_valid() and
                info_form.is_valid() and
                address_form.is_valid()):

            new_bank_account = bank_account_form.save()
            new_address = address_form.save()

            new_info = info_form.save(commit=False)
            new_info.address = new_address
            new_info.bank_account = new_bank_account
            info_form.save()

            new_user = user_form.save(commit=False)
            new_user.info = new_info
            user_form.save()

            # login and redirect
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse('core:profile'))
    else:
        if request.user.is_authenticated:
            return redirect(reverse('core:profile'))
        else:
            user_form = UserBaseForm()
            info_form = InfoForm()
            address_form = AddressForm()
            bank_account_form = BankAccountForm()

    context = {
        'user_form': user_form,
        'info_form': info_form,
        'address_form': address_form,
        'bank_account_form': bank_account_form,
    }

    return render(request, 'core/account/register.html', context)


def custom_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('core:profile'))
    else:
        return LoginView.as_view(
            template_name='core/account/login.html')(request)


def profile(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user_info = User.objects.select_related().get(id=user_id)
        form = UserBaseForm({'first_name': 'test'})

        context = {'form': form}
        return render(request, 'core/account/profile.html', context)
    else:
        return redirect(reverse('core:login'))
