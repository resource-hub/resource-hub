from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from core.forms import SignUpForm


def index(request):
    return render(request, 'core/index.html')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('')
    else:
        form = SignUpForm()
    return render(request, 'core/register.html', {'form': form})


def profile(request):
    return render(request, 'core/profile.html')
